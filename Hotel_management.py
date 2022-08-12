#uvozimo bottle
from ctypes import get_last_error
from bottle import *
from bottleext import *

#import sqlite3
import hashlib
import os

#uvozimo potrebne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2 - nalozi v ukaznem pozivu pip install psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

#privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

#conn_datoteka = 'HotelManagement.db'
# odkomentiraj, če želiš sporočila o napakah
debug(True)

def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    # idk zaki spodaj zakomentirano - iza ma tk
    if sporocilo is None:
        response.delete_cookie('sporocilo')
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

def preveriUporabnika(): 
   username = request.get_cookie("username", secret=skrivnost)
   if username:
       cur = conn.cursor()    
       uporabnik = None
       try: 
           uporabnik = cur.execute("SELECT * FROM zaposleni WHERE username = %s", (username, )).fetchone()
       except:
           uporabnik = None
       if uporabnik: 
           return uporabnik
   redirect('/prijava')

#------------------------------------------------
#FUNKCIJE ZA IZGRADNJO STRANI
# @route("/static/<filename:path>")
# def static(filename):
#     return static_file(filename, root=static_dir)

#-----------------------------------------------
#ZAČETNA STRAN
#-----------------------------------------------
@get('/')
def index():
    return template('prijava.html')

@get('/dashboard')
def dashboard():
    return template('dashboard.html')
#------------------------------------------------


#------------------------------------------------
# REGISTRACIJA, PRIJAVA, ODJAVA
#------------------------------------------------

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

@get('/registracija')
def registracija_get():
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka)

@post('/registracija')
def registracija_post():
    ime = request.forms.ime
    username = request.forms.username
    password = request.forms.password
    password2 = request.forms.password2

    print(ime, username, password, password2)

    if (ime == '') or (username == '') or (password == '') or (password2 == ''): 
        nastaviSporocilo('Registracija ni možna, ker dobim prazen string.') 
        #redirect('/registracija')
        redirect(url('registracija_get'))
        #return None #  brezveze
    # cur = conn.cursor()     # je že vspostavljen ne rabim še enkrat
    #uporabnik = None #  to je mal brezveze
    # try: 
    try:
        cur.execute(f"SELECT * FROM zaposleni WHERE ime = \'{ime}\'")
        uporabnik = cur.fetchone()
        print(uporabnik)
    except Exception:
        conn.rollback()
        # nared neki če ga ni
        nastaviSporocilo('Registracija ni možna, uporabnik ni v bazi.') 
        #redirect('/registracija')
        redirect(url('registracija_get'))
    #     print(e)
    #     uporabnik = None
    # if uporabnik is None:
    #     nastaviSporocilo('Registracija ni možna, uporabnik ni v bazi.') 
    #     #redirect('/registracija')
    #     redirect(url('registracija_get'))
    #     return
    if len(password) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.') 
        #redirect('/registracija')
        redirect(url('registracija_get'))

    if password != password2:
        nastaviSporocilo('Gesli se ne ujemata.') 
        #redirect('/registracija')
        redirect(url('registracija_get'))

    zgostitev = hashGesla(password)
    #cur.execute("UPDATE zaposleni set username = %s, password = %s WHERE ime = %s", (username, zgostitev, ime))
    try:
        # cur.execute("""INSERT INTO zaposleni
        #             (ime, username, password)
        #             VALUES (%s, %s, %s)""", (ime, username, zgostitev))
        cur.execute(f"""UPDATE zaposleni
                        SET
                            username = \'{username}\',
                            password = \'{zgostitev}\'
                        WHERE
                            ime = \'{ime}\'""")
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        #redirect('/registracija')
        redirect(url('registracija_get'))

    response.set_cookie('username', username, secret=skrivnost)
    print('vrzem vas na zaposlene')
    redirect('/prijava')



@get('/prijava')
def prijava_get():
   napaka = nastaviSporocilo()
   return template('prijava.html', napaka=napaka)

@post('/prijava')
def prijava_post():
   username = request.forms.username
   password = request.forms.password
   if (username=='') or (password==''):
       nastaviSporocilo('Uporabniško ima in geslo morata biti neprazna') 
       redirect('/prijava')

#    cur = conn.cursor()    
#    hashconn = None
   try: 
       cur.execute("SELECT password FROM zaposleni WHERE username = %s", (username, ))
       hashconn = cur.fetchone()
       hashconn = hashconn[-1]  # ne dodajaj kolon na desno
   except:
        conn.rollback()
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect('/prijava')

   if hashGesla(password) != hashconn:
       nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
       redirect('/prijava')
       

   response.set_cookie('username', username, secret=skrivnost)
   redirect('/dashboard')
    
@get('/odjava')
def odjava_get():
   response.delete_cookie('username')
   redirect('/prijava')
#-----------------------------------------------------------------------------------------
# ZAPOSLENI
#-----------------------------------------------------------------------------------------

@get('/zaposleni')
def zaposleni():
    #cur = conn.cursor()
    cur.execute("ROLLBACK")
    zaposleni = cur.execute("""SELECT ime,priimek,naziv,oddelek.oddelek_ime,naslov.mesto, naslov.posta, naslov.drzava,hotel_podatki.ime_hotela FROM Zaposleni
            JOIN naslov ON Zaposleni.naslov_id=naslov.naslov_id
            JOIN hotel_podatki ON Zaposleni.hotel_id=hotel_podatki.hotel_id
            JOIN oddelek ON Zaposleni.oddelek_id=oddelek.oddelek_id
            ORDER BY Zaposleni.priimek, Zaposleni.ime""")
    cur.fetchone()
    return template('zaposleni.html', zaposleni=cur)

@get('/dodaj_zaposlenega')
def dodaj_zaposlenega():
   return template('dodaj_zaposlenega.html', zaposleni_id='', ime='', priimek='', naziv='', telefonska_stevilka='', email='', oddelek_id='', naslov_id='', hotel_id='', username='', password='', napaka=None)

@post('/dodaj_zaposlenega')
def dodaj_zaposlenega_post():
#    zaposleni_id = request.forms.zaposleni_id
   ime = request.forms.ime
   priimek = request.forms.priimek
   naziv = request.forms.naziv
   telefonska_stevilka = request.forms.telefonska_stevilka
   email = request.forms.email
   oddelek = request.forms.oddelek
   mesto = request.forms.mesto
   drzava = request.forms.drzava
   posta = request.forms.posta
   hotel = request.forms.hotel
#    username = request.forms.username
#    password = request.forms.password
#    password2 = hashGesla(password2)
   print(ime, priimek, naziv, mesto, posta, drzava, telefonska_stevilka, email, oddelek)
   
   cur.execute("""INSERT INTO naslov
                (mesto, posta, drzava)
                VALUES (%s, %s, %s)""", (mesto, posta, drzava))
   conn.commit()
   conn.rollback()


#    cur.execute("""INSERT INTO naslov
#                 (mesto, posta, drzava)
#                 VALUES (%s, %s, %s)""", (mesto, posta, drzava))
#    conn.commit()
#    conn.rollback()

#    print('insertov sem oddelek')

   cur.execute("""SELECT naslov_id FROM naslov WHERE mesto = %s """,(mesto,))
   naslov_id = cur.fetchall()[0][0]

   cur.execute("""SELECT hotel_id FROM hotel_podatki WHERE ime_hotela = %s """,(hotel,))
   hotel_id = cur.fetchall()[0][0]
   print('tale id za hotel:')
   print(hotel_id)

   cur.execute("""SELECT oddelek_id FROM oddelek WHERE oddelek_ime = %s """,(oddelek,))
   oddelek_id = cur.fetchall()[0][0]
   print('tale id za oddelek:')
   print(oddelek_id)   

   
   cur.execute("""INSERT INTO zaposleni
               (ime, priimek, naziv, naslov_id, hotel_id, oddelek_id, telefonska_stevilka, email)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s )""", (ime, priimek, naziv, naslov_id, hotel_id, oddelek_id, telefonska_stevilka, email))
   conn.commit()
   conn.rollback()   
   redirect(url('zaposleni'))


@get('/izbrisi_zaposlenega')
def izbrisi_zaposlenega():
   return template('izbrisi_zaposlenega.html', gostje_id='', ime='', priimek='', kreditna_kartica='', email='', telefonska_stevilka='', naslov_id='', napaka=None)


@post('/izbrisi_zaposlenega')
def izbrisi_zaposlenega_post():
#    zaposleni_id = request.forms.zaposleni_id
   ime = request.forms.ime
   priimek = request.forms.priimek
#    kreditna_kartica = request.forms.kreditna_kartica
   telefonska_stevilka = request.forms.telefonska_stevilka
#    email = request.forms.email
#    mesto = request.forms.mesto
#    drzava = request.forms.drzava
#    posta = request.forms.posta
   print(ime, priimek, telefonska_stevilka)

   # izbrisati moram tudi vrstico v rezervacijah kjer je id zaposlenega
   cur.execute("""SELECT zaposleni_id FROM zaposleni WHERE (ime, priimek, telefonska_stevilka) = (%s, %s, %s) """,(ime, priimek, telefonska_stevilka))
   zaposleni_id = cur.fetchall()[0][0]
   print('tale id za hotel:')
   print(zaposleni_id)  

   cur.execute("""DELETE FROM rezervacije
                  WHERE zaposleni_id = %s""", (zaposleni_id,))
   conn.commit()
   conn.rollback() 

   cur.execute("""DELETE FROM zaposleni
                  WHERE (ime, priimek, telefonska_stevilka) = (%s, %s, %s)""", (ime, priimek, telefonska_stevilka))

   conn.commit()
   conn.rollback() 
             

   redirect(url('zaposleni'))


#----------------------------------------------------------------------------------------
# HOTELSKA VERIGA
#-----------------------------------------------------------------------------------------

@get('/hotelska_veriga')
def hotelska_veriga():
    # cur = conn.cursor()
    cur.execute("ROLLBACK")
    cur.execute("""SELECT ime_hotelske_verige, naslov.mesto, naslov.posta, naslov.drzava, email_hotelske_verige, spletna_stran FROM hotelska_veriga
        JOIN naslov ON hotelska_veriga.naslov_glavne_pisarne=naslov.naslov_id""")
    cur.fetchone()
    return template('hotelska_veriga.html', hotelska_veriga=cur)


#-------------------------------------------------------------------------------------------
# HOTEL
#------------------------------------------------------------------------------------------

@get('/hotel')
def hotel():
    #cur = conn.cursor()
    cur.execute("ROLLBACK")
    cur.execute("""SELECT ime_hotela, naslov.mesto, naslov.posta, naslov.drzava, telefonska_stevilka, email, hotelska_veriga.ime_hotelske_verige FROM hotel_podatki
        JOIN naslov ON hotel_podatki.naslov_id=naslov.naslov_id
        JOIN hotelska_veriga ON hotel_podatki.hotelska_veriga_id=hotelska_veriga.hotelska_veriga_id
        ORDER BY hotel_podatki.ime_hotela""")
    cur.fetchone()
    return template('hotel.html', hotel=cur)


#---------------------------------------------------------------------------------------
# GOST
#---------------------------------------------------------------------------------------

@get('/gostje')
def gostje():
    #cur = conn.cursor()
    cur.execute("ROLLBACK")
    cur.execute("""SELECT ime,priimek,telefonska_stevilka,email,naslov.mesto, naslov.posta, naslov.drzava FROM gostje
        JOIN naslov ON gostje.naslov_id=naslov.naslov_id
        ORDER BY gostje.priimek""")
    cur.fetchone()
    return template('gostje.html', gostje=cur)

@get('/dodaj_gosta')
def dodaj_gosta():
   return template('dodaj_gosta.html', gostje_id='', ime='', priimek='', kreditna_kartica='', email='', telefonska_stevilka='', naslov_id='', napaka=None)


@post('/dodaj_gosta')
def dodaj_gosta_post():
#    zaposleni_id = request.forms.zaposleni_id
   ime = request.forms.ime
   priimek = request.forms.priimek
   kreditna_kartica = request.forms.kreditna_kartica
   telefonska_stevilka = request.forms.telefonska_stevilka
   email = request.forms.email
   mesto = request.forms.mesto
   drzava = request.forms.drzava
   posta = request.forms.posta
   print(ime, priimek, kreditna_kartica, mesto, posta, drzava, telefonska_stevilka, email)
   
   cur.execute("""INSERT INTO naslov 
                (mesto, posta, drzava) 
                VALUES (%s, %s, %s)""", (mesto, posta, drzava))
                
   conn.commit()
   conn.rollback()

   cur.execute("""SELECT naslov_id FROM naslov WHERE mesto = %s """,(mesto,))
   naslov_id = cur.fetchall()[0][0]

#    cur.execute("""SELECT hotel_id FROM hotel_podatki WHERE ime_hotela = %s """,(hotel,))
#    hotel_id = cur.fetchall()[0][0]
#    print('tale id za hotel:')
#    print(hotel_id)

#    cur.execute("""SELECT oddelek_id FROM oddelek WHERE oddelek_ime = %s """,(oddelek,))
#    oddelek_id = cur.fetchall()[0][0]
#    print('tale id za oddelek:')
#    print(oddelek_id)  

   #cur.execute("""SELECT setval('gostje_gostje_id_seq', (SELECT MAX(gostje_id) FROM gostje)+1)""")

   
   cur.execute("""INSERT INTO gostje
               (ime, priimek, kreditna_kartica, email, telefonska_stevilka, naslov_id)
               VALUES (%s, %s, %s, %s, %s, %s)""", (ime, priimek, kreditna_kartica, email, telefonska_stevilka, naslov_id))
   conn.commit()
   conn.rollback()   
   redirect(url('gostje'))


@get('/izbrisi_gosta')
def izbrisi_gosta():
   return template('izbrisi_gosta.html', gostje_id='', ime='', priimek='', kreditna_kartica='', email='', telefonska_stevilka='', naslov_id='', napaka=None)


@post('/izbrisi_gosta')
def izbrisi_gosta_post():
#    zaposleni_id = request.forms.zaposleni_id
   ime = request.forms.ime
   priimek = request.forms.priimek
#    kreditna_kartica = request.forms.kreditna_kartica
   telefonska_stevilka = request.forms.telefonska_stevilka
#    email = request.forms.email
#    mesto = request.forms.mesto
#    drzava = request.forms.drzava
#    posta = request.forms.posta
   print(ime, priimek, telefonska_stevilka)

   # izbrisati moram tudi vrstico v rezervacijah kjer je id gosta
   cur.execute("""SELECT gostje_id FROM gostje WHERE (ime, priimek, telefonska_stevilka) = (%s, %s, %s) """,(ime, priimek, telefonska_stevilka))
   gostje_id = cur.fetchall()[0][0]
   print('tale id brišem:')
   print(gostje_id)  

   cur.execute("""DELETE FROM rezervacije
                  WHERE gostje_id = %s""", (gostje_id,))
   conn.commit()
   conn.rollback()

   cur.execute("""DELETE FROM gostje
                  WHERE (ime, priimek, telefonska_stevilka) = (%s, %s, %s)""", (ime, priimek, telefonska_stevilka))

   conn.commit()
   conn.rollback()   
   redirect(url('gostje'))
   

### SOBA

@get('/sobe')
def sobe():
    #cur = conn.cursor()
    cur.execute("ROLLBACK")
    cur.execute("""SELECT stevilka_sobe,tip_sobe_id,hotel_podatki.ime_hotela FROM sobe
        JOIN hotel_podatki ON sobe.hotel_id=hotel_podatki.hotel_id""")
    cur.fetchone()
    return template('sobe.html', sobe=cur)

### HOTELSKA STORITEV

@get('/hotelske_storitve')
def hotelske_storitve():
    #cur = conn.cursor()
    cur.execute("ROLLBACK")
    cur.execute("""SELECT naziv_storitve,opis_storitve,cena_storitve,hotel_podatki.ime_hotela FROM hotelske_storitve
        JOIN hotel_podatki ON hotelske_storitve.hotel_id=hotel_podatki.hotel_id
        ORDER BY hotelske_storitve.cena_storitve""")
    cur.fetchone()
    return template('hotelske_storitve.html', hotelske_storitve=cur)


@get('/dodaj_storitev')
def dodaj_storitev():
   return template('dodaj_storitev.html',hotelske_storitve_id='',naziv_storitve='',opis_storitve='',cena_storitve='',hotel_id='', napaka=None)


@post('/dodaj_storitev')
def dodaj_storitev_post():
   naziv_storitve = request.forms.naziv_storitve
   opis_storitve = request.forms.opis_storitve
   cena_storitve = request.forms.cena_storitve
   hotel = request.forms.hotel
                
   conn.commit()
   conn.rollback()

   cur.execute("""SELECT hotel_id FROM hotel_podatki WHERE ime_hotela = %s """,(hotel,))
   hotel_id = cur.fetchall()[0][0]

   cur.execute("""INSERT INTO hotelske_storitve
               (naziv_storitve, opis_storitve, cena_storitve, hotel_id)
               VALUES (%s, %s, %s, %s)""", (naziv_storitve, opis_storitve, cena_storitve, hotel_id))
   conn.commit()
   conn.rollback()   
   redirect(url('hotelske_storitve'))

@get('/izbrisi_storitev')
def izbrisi_storitev():
   return template('izbrisi_storitev.html',hotelske_storitve_id='',naziv_storitve='',opis_storitve='',cena_storitve='',hotel_id='', napaka=None)

@post('/izbrisi_storitev')
def izbrisi_storitev_post():
   naziv_storitve = request.forms.naziv_storitve
   #opis_storitve = request.forms.opis_storitve
   #cena_storitve = request.forms.cena_storitve
   #hotel = request.forms.hotel

   #cur.execute("""DELETE FROM Zaposleni WHERE hotel_id = %s""", (hotel_id))
   #conn.commit()
   #conn.rollback()
   
   #cur.execute("""DELETE FROM sobe WHERE hotel_id = %s""", (hotel_id))
   #conn.commit()
   #conn.rollback()
   
   #cur.execute("""DELETE FROM rezervacije WHERE hotel_id = %s""", (hotel_id))
   #conn.commit()
   #conn.rollback()
   
   cur.execute("""DELETE FROM hotelske_storitve WHERE naziv_storitve = %s""",(naziv_storitve))
   conn.commit()
   conn.rollback()   
   redirect(url('hotelske_storitve'))


### UPORABLJENE STORITVE

@get('/uporabljene_storitve')
def uporabljene_storitve():
    #cur = conn.cursor()
    cur.execute("ROLLBACK")
    cur.execute("""SELECT hotelske_storitve.naziv_storitve, hotelske_storitve.opis_storitve, hotelske_storitve.cena_storitve, hotel_podatki.ime_hotela FROM uporabljene_storitve
        JOIN hotelske_storitve ON uporabljene_storitve.hotelske_storitve_id=hotelske_storitve.hotelske_storitve_id
        JOIN hotel_podatki ON hotelske_storitve.hotel_id=hotel_podatki.hotel_id
        ORDER BY hotelske_storitve.cena_storitve""")
    cur.fetchone()
    return template('uporabljene_storitve.html', uporabljene_storitve=cur)

@get('/uporabi_storitev')
def uporabi_storitev():
   return template('uporabi_storitev.html',hotelske_storitve_id='',naziv_storitve='',opis_storitve='',cena_storitve='',hotel_id='', napaka=None)


@post('/uporabi_storitev')
def uporabi_storitev_post():
   hotelske_storitve= request.forms.hotelske_storitve
                
   conn.commit()
   conn.rollback()

   cur.execute("""SELECT hotelske_storitve_id FROM hotelske_storitve WHERE (naziv_storitve, opis_storitve, cena_storitve) = (%s, %s, %s) """,(hotelske_storitve,))
   hotelske_storitve_id = cur.fetchall()[0][0]


   cur.execute("""INSERT INTO uporabljene_storitve
               (rezervacije_id, hotelske_storitve_id)
               VALUES (%s, %s)""", (rezervacije_id, hotelske_storitve_id))
   conn.commit()
   conn.rollback()   
   redirect(url('hotelske_storitve'))

# ### OSTALO

# # conn = sqlite3.connect(conn_datoteka, isolation_level=None)
# # conn.set_trace_callback(print)
# # cur = conn.cursor()
# # cur.execute("PRAGMA foreign_keys = ON;")
# # run(host='localhost', port=8080, reloader=True)


# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) #za pogovarjanje z bazo

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
    print('test')
