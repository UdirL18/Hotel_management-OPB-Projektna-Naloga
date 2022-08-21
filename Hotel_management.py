#uvozimo bottle
#import sqlite3
import hashlib
import os
#from ctypes import get_last_error
from datetime import datetime

# uvozimo psycopg2 - nalozi v ukaznem pozivu pip install psycopg2
import psycopg2
import psycopg2.extensions
import psycopg2.extras

#uvozimo potrebne podatke za povezavo
import auth_public as auth
from bottle import *
from bottleext import *

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
   redirect(url('prijava'))

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
    return template('dashboard.html', dashboard=cur)

@route('/dashboard')
def dashboard():
    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM hotelska_veriga""")
    vsota = cur.fetchone()
    
    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM hotel_podatki""")
    vsota1 = cur.fetchone()

    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM zaposleni""")
    vsota2 = cur.fetchone()

    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM gostje""")
    vsota3 = cur.fetchone()

    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM sobe""")
    vsota4 = cur.fetchone()

    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM rezervirane_sobe""")
    vsota5 = cur.fetchone()

    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM hotelske_storitve""")
    vsota7 = cur.fetchone()

    cur.execute("ROLLBACK")
    cur.execute("""SELECT COUNT(*) FROM uporabljene_storitve""")
    vsota8 = cur.fetchone()

    return template('dashboard.html', vsota=vsota, vsota1=vsota1, vsota2=vsota2, vsota3=vsota3, vsota4=vsota4, vsota5=vsota5,vsota7=vsota7,vsota8=vsota8)  # your template file is form1.tpl
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
       nastaviSporocilo('Uporabniško ime in geslo morata biti neprazna') 
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
    cur.execute("""SELECT stevilka_sobe,hotel_podatki.ime_hotela, tipi_sob.tip_sobe_opis FROM sobe
            JOIN hotel_podatki ON sobe.hotel_id=hotel_podatki.hotel_id
            JOIN tipi_sob ON sobe.tip_sobe_id=tipi_sob.tip_sobe_id""")
    cur.fetchone()
    return template('sobe.html', sobe=cur)

# rezerviraj sobo
# -naj izpise tabelo prostih sob - če je soba na seznamu rezervirane_sobe ni prosta,
#   tabelo, ki jo izpise naj vklučuje tudi št postelj, opis sobe, ceno sobe, v katerem hotelu
# -klikni na izbrano sobo da te vrže na stran rezerviraj
# -v rezervaciji naj se podatki sobe shranijo sami, vpišeš le tip_plačila, datum_rezervacije - bi slo da to sam now(),
#   st_rezerviranih_sob - naj izpolne program (vse bo 1), datum_check_in, datum_check_out,
# -predn lahko zaposleni izvede registracijo naj vpiše svoje ime in priimek-da dobim zaposleni_id, 
#   potem naj vpiše ime in priimek gosta, ki je že prijavljen, če ni naj ga registrira, da dobim gostje_id
# -hotel_id naj se prebere iz podatkov izbrane sobe

@get('/rezerviraj_sobo')
def rezerviraj_sobo():
   return template('rezerviraj_sobo.html', rezervacije_id = '', tip_placila = '', datum_rezervacije = '', st_rezerviranih_sob = '', datum_check_in = '', datum_check_out = '', zaposleni_id = '', gostje_id = '', hotel_id = '' )


@get('/rezerviraj_sobo', methods=['GET', 'POST'])
def rezerviraj_sobo():
    print(request.method)
    #cur = conn.cursor()
    cur.execute("ROLLBACK")
    cur.execute("""SELECT DISTINCT stevilka_sobe, tipi_sob.tip_sobe_opis, tipi_sob.tip_sobe_ime, tipi_sob.cena_sobe, tipi_sob.zivali, tipi_sob.kadilci, hotel_podatki.ime_hotela FROM sobe
            JOIN hotel_podatki ON sobe.hotel_id=hotel_podatki.hotel_id
            JOIN tipi_sob ON sobe.tip_sobe_id=tipi_sob.tip_sobe_id
            WHERE soba_id NOT IN (SELECT DISTINCT sobe_id FROM rezervirane_sobe)""")
    cur.fetchone()
    return template('rezerviraj_sobo.html', sobe=cur)


@get('/rezervacija')
def rezervacija():
   napaka = nastaviSporocilo()
   cur.execute("ROLLBACK")
   cur.execute("""SELECT ime_hotela FROM hotel_podatki""")
   cur.fetchone()
   return template('rezervacija.html', ime_zaposlenega='', priimek_zaposlenega='', ime_gosta='', priimek_gosta='', napaka=napaka, hotel=cur)

def preveriZaposlenega(ime_zaposlenega, priimek_zaposlenega): 
   cur.execute("""SELECT zaposleni_id FROM zaposleni WHERE (ime, priimek) = (%s, %s) """,(ime_zaposlenega, priimek_zaposlenega,))
   zaposleni_id = cur.fetchall()
   if len(zaposleni_id) == 0:
    return False
   return True

def preveriGosta(ime_gosta, priimek_gosta): 
   cur.execute("""SELECT gostje_id FROM gostje WHERE (ime, priimek) = (%s, %s ) """,(ime_gosta, priimek_gosta,))
   gostje_id = cur.fetchall()
   if len(gostje_id) == 0:
    return False
   return True   

@post('/rezervacija')
def rezervacija_post():
   ime_zaposlenega = request.forms.ime_zaposlenega
   priimek_zaposlenega = request.forms.priimek_zaposlenega
   ime_gosta = request.forms.ime_gosta
   priimek_gosta = request.forms.priimek_gosta
   zaposlen = preveriZaposlenega(ime_zaposlenega, priimek_zaposlenega)
   gost = preveriGosta(ime_gosta, priimek_gosta)
   datum_rezervacije = datetime.today().strftime('%Y-%m-%d')
   tip_placila = request.forms.tip_placila
   datum_check_in = request.forms.datum_check_in
   datum_check_out = request.forms.datum_check_out
   st_rezerviranih_sob = 1
   stevilka_sobe = request.forms.stevilka_sobe
   ime_hotela = request.forms.ime_hotela


   print(ime_zaposlenega, priimek_zaposlenega, ime_gosta, priimek_gosta, datum_rezervacije, tip_placila, datum_check_in, datum_check_out, st_rezerviranih_sob, stevilka_sobe, ime_hotela)

   if not zaposlen:
      nastaviSporocilo('Zaposleni ni na seznamu.')
      redirect('/rezervacija')

   if not gost:
      nastaviSporocilo('Gost ni na seznamu.')
      redirect('/rezervacija')    

   cur.execute("""SELECT zaposleni_id FROM zaposleni WHERE (ime, priimek) = (%s, %s) """,(ime_zaposlenega, priimek_zaposlenega,))
   zaposleni_id = cur.fetchall()[0][0]


   cur.execute("""SELECT gostje_id FROM gostje WHERE (ime, priimek) = (%s, %s) """,(ime_gosta, priimek_gosta,))
   gostje_id = cur.fetchall()[0][0]

   cur.execute("""SELECT hotel_id FROM hotel_podatki WHERE ime_hotela = %s""",(ime_hotela.replace('_',' '),))
   hotel_id = cur.fetchall()[0][0]
   
   cur.execute("""INSERT INTO rezervacije
               (tip_placila, datum_rezervacije, st_rezerviranih_sob, datum_check_in, datum_check_out, zaposleni_id, gostje_id, hotel_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (tip_placila, datum_rezervacije, st_rezerviranih_sob, datum_check_in, datum_check_out, zaposleni_id, gostje_id, hotel_id))
   conn.commit()
   conn.rollback() 

   cur.execute("""SELECT soba_id FROM sobe WHERE stevilka_sobe = %s""",(stevilka_sobe,))
   sobe_id = cur.fetchall()[0][0]   

   cur.execute("""SELECT rezervacije_id FROM rezervacije WHERE (tip_placila, datum_rezervacije, st_rezerviranih_sob, datum_check_in, datum_check_out, zaposleni_id, gostje_id, hotel_id) = (%s, %s, %s, %s, %s, %s, %s, %s)""",(tip_placila, datum_rezervacije, st_rezerviranih_sob, datum_check_in, datum_check_out, zaposleni_id, gostje_id, hotel_id))
   rezervacije_id = cur.fetchall()[0][0]    

   cur.execute("""INSERT INTO rezervirane_sobe
               (rezervacije_id, sobe_id)
               VALUES (%s, %s)""", (rezervacije_id, sobe_id))
   conn.commit()
   conn.rollback()   
   redirect(url('sobe'))

#-----------------------------------------------------------------------------------------------
### HOTELSKA STORITEV
#------------------------------------------------------------------------------------------

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
   nazivstoritve = request.forms.naziv_storitve
   #opis_storitve = request.forms.opis_storitve
   #cena_storitve = request.forms.cena_storitve
   #hotel = request.forms.hotel

   print(request.forms.naziv_storitve)
   cur.execute("""SELECT hotelske_storitve_id FROM hotelske_storitve WHERE naziv_storitve = %s""",(nazivstoritve,))
   hotelske_storitve_id = cur.fetchall()[0][0]


   #cur.execute("""DELETE FROM Zaposleni WHERE hotel_id = %s""", (hotel_id))
   #conn.commit()
   #conn.rollback()
   
   #cur.execute("""DELETE FROM sobe WHERE hotel_id = %s""", (hotel_id))
   #conn.commit()
   #conn.rollback()
   
   #cur.execute("""DELETE FROM rezervacije WHERE hotel_id = %s""", (hotel_id))
   #conn.commit()
   #conn.rollback()

   cur.execute("""DELETE FROM uporabljene_storitve WHERE hotelske_storitve_id = %s""", (hotelske_storitve_id,))
   conn.commit()
   conn.rollback()
   
   cur.execute("""DELETE FROM hotelske_storitve WHERE naziv_storitve = %s""",(nazivstoritve,))
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
   rezervacije_id = request.forms.rezervacije_id
   hotelske_storitve_id= request.forms.hotelske_storitve_id
                
   conn.commit()
   conn.rollback()

   cur.execute("""SELECT rezervacije_id FROM rezervacije WHERE rezervacije_id = %s""",(rezervacije_id,))
   rezervacije_id = cur.fetchall()[0][0]


   cur.execute("""SELECT hotelske_storitve_id FROM hotelske_storitve WHERE (hotelske_storitve_id) = %s """,(hotelske_storitve_id,))
   hotelske_storitve_id = cur.fetchall()[0][0]

   conn.commit()
   conn.rollback()

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
