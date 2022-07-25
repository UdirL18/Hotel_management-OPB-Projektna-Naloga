from bottle import *
from bottleext import *
import sqlite3
import hashlib
import os

baza_datoteka = 'HotelManagement.db'
debug(True)

def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo')
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

#def preveriUporabnika(): 
#    username = request.get_cookie("username", secret=skrivnost)
#    if username:
#        cur = baza.cursor()    
#        uporabnik = None
#        try: 
#            uporabnik = cur.execute("SELECT * FROM oseba WHERE username = ?", (username, )).fetchone()
#        except:
#            uporabnik = None
#        if uporabnik: 
#            return uporabnik
#    redirect('/prijava')

@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)

@get('/')
def index():
    return template('zacetna_stran.html')

### ZAPOSLENI
@get('/zaposleni')
def zaposleni():
    cur = baza.cursor()
    zaposleni = cur.execute("SELECT zaposleni_id,ime,priimek,naziv,telefonska_stevilka,email,oddelek_id,naslov_id,hotel_id FROM zaposleni")
    return template('zaposleni.html', zaposleni=zaposleni)

@get('/dodaj_zaposlenega')
def dodaj_zaposlenega():
    return template('dodaj_zaposlenega.html', zaposleni_id='', ime='', priimek='', naziv='', telefonska_stevilka='', email='', oddelek_id='', naslov_id='', hotel_id='', username='', password='', napaka=None)

@post('/dodaj_zaposlenega')
def dodaj_zaposlenega_post():
    zaposleni_id = request.forms.zaposleni_id
    ime = request.forms.ime
    priimek = request.forms.priimek
    naziv = request.forms.naziv
    telefonska_stevilka = request.forms.telefonska_stevilka
    email = request.forms.email
    oddelek_id = request.forms.oddelek_id
    naslov_id = request.forms.naslov_id
    hotel_id = request.forms.hotel_id
    username = request.forms.username
    password = request.forms.password
    password2 = hashGesla(password2)

    cur.execute("""INSERT INTO zaposleni
                (zaposleni_id,ime,priimek,naziv,telefonska_stevilka,email,oddelek_id,naslov_id,hotel_id, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (zaposleni_id,ime,priimek,naziv,telefonska_stevilka,email,oddelek_id,naslov_id,hotel_id, username, password2))
    redirect(url('zaposleni'))

#@get('/zaposleni/dodaj')
#def dodaj_komitenta_get():
#    return template('zaposleni-edit.html')

#@post('/zaposleni/dodaj') 
#def dodaj_zaposleni():
#    zaposleni_id = request.forms.zaposleni_id
#    ime = request.forms.ime
#    priimek = request.forms.priimek
#    email = request.forms.email
#    naziv = request.forms.naziv
#    telefonska_stevilka = request.forms.telefonska_stevilka
#    naslov_id = request.forms.naslov_id
#    hotel_id = request.forms.hotel_id
#    oddelek_id = request.forms.oddelek_id
#    cur = baza.cursor()
#    cur.execute("INSERT INTO zaposleni (zaposleni_id, ime, priimek, naziv, telefonska_stevilka, email,oddelek_id, naslov_id, hotel_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (zaposleni_id, ime, priimek, naziv, telefonska_stevilka, email,oddelek_id, naslov_id, hotel_id))
#    redirect('/zaposleni')

### HOTELSKA VERIGA

@get('/hotelska_veriga')
def hotelska_veriga():
    cur = baza.cursor()
    hotelska_veriga = cur.execute("SELECT ime_hotelske_verige, naslov_glavne_pisarne FROM hotelska_veriga")
    return template('hotelska_veriga.html', hotelska_veriga=hotelska_veriga)

### REGISTRACIJA, PRIJAVA

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
    zaposleni_id = request.forms.zaposleni_id
    username = request.forms.username
    password = request.forms.password
    password2 = request.forms.password2
    if zaposleni_id is None or username is None or password is None or password2 is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    cur = baza.cursor()    
    uporabnik = None
    try: 
        uporabnik = cur.execute("SELECT * FROM zaposleni WHERE zaposleni_id = ?", (zaposleni_id, )).fetchone()
    except:
        uporabnik = None
    if uporabnik is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    if len(password) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.') 
        redirect('/registracija')
        return
    if password != password2:
        nastaviSporocilo('Gesli se ne ujemata.') 
        redirect('/registracija')
        return
    zgostitev = hashGesla(password)
    cur.execute("UPDATE zaposleni set username = ?, password = ? WHERE zaposleni_id = ?", (username, zgostitev, zaposleni_id))
    response.set_cookie('username', username, secret=skrivnost)
    redirect('/zaposleni')



#@get('/prijava')
#def prijava_get():
#    napaka = nastaviSporocilo()
#    return template('prijava.html', napaka=napaka)

#@post('/prijava')
#def prijava_post():
#    username = request.forms.username
#    password = request.forms.password
#    if username is None or password is None:
#        nastaviSporocilo('Uporabniško ima in geslo morata biti neprazna') 
#        redirect('/prijava')
#        return
#    cur = baza.cursor()    
#    hashBaza = None
#    try: 
#        hashBaza = cur.execute("SELECT password FROM oseba WHERE username = ?", (username, )).fetchone()
#        hashBaza = hashBaza[0]
#    except:
#        hashBaza = None
#    if hashBaza is None:
#        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
#        redirect('/prijava')
#        return
#    if hashGesla(password) != hashBaza:
#        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
#        redirect('/prijava')
#        return
#    response.set_cookie('username', username, secret=skrivnost)
#    redirect('/komitenti')
    
#@get('/odjava')
#def odjava_get():
#    response.delete_cookie('username')
#    redirect('/prijava')

### OSTALO

baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print)
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
run(host='localhost', port=8080, reloader=True)
