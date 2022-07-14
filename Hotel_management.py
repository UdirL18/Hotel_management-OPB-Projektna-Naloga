#===================================================================================
# SPLETNA APIKACIJA HOTEL MANAGEMENT
#===============================================================================
# Za izdelavo potrebujemo bottle
from bottleext import *
import sqlite3
import hashlib

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
#import psycopg2, psycopg2.extensions, psycopg2.extras
#psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
import hashlib

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# KONFIGURACIJA
baza_datoteka = 'HotelManagement.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju

# # napakaSporocilo = None

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo') #če funkciji ne podamo ničesar, izbriše piškotek z imenom sporočilo
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro 
    
# # Mapa za statične vire (slike, css, ...)
# static_dir = "./static"

# skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"
# # streženje statičnih datotek

@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)

# Statične datoteke damo v mapo 'static' in do njih pridemo na naslovu '/static/...'
# Uporabno za slike in CSS, poskusi http://localhost:8080/static/slika.jpg
@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

# ---------------------------------------------
# !!!ali je smiselno sploh imeti prijavo
# --------------------------------------------
# def preveriUporabnika(): 
#     username = request.get_cookie("username", secret=skrivnost)
#     if username:
#         cur = baza.cursor()    
#         uporabni = None
#         try: 
#             uporabnik = cur.execute("SELECT * FROM oseba WHERE username = ?", (username, )).fetchone()
#         except:
#             uporabnik = None
#         if uporabnik: 
#             return uporabnik
#     redirect('/prijava')


# def preveriUporabnika(): 
#     ime = request.get_cookie("ime", secret=skrivnost)
#     if ime:
#        # cur = baza.cursor()    
#         uporabnik = None
#         try: 
#             cur.execute("SELECT * FROM gostje WHERE ime = %s", [ime])
#             uporabnik = cur.fetchone()
#         except:
#             uporabnik = None
#         if uporabnik: 
#             return uporabnik
#     redirect(url('prijava_get'))

@get('/')
def index():
    nastaviSporocilo('Pozdravljeni v e-Hotel. V kolikor še niste naš član, se prosim registrirajte.')
    napaka = request.get_cookie('sporocilo', secret=skrivnost)
    uporabnik = request.get_cookie('uporabnik', secret=skrivnost)
    return template('zacetna_stran.html', uporabnisko_ime='', geslo='', napaka = napaka, uporabnik = uporabnik)


#------------------------------------------
# Hotelska_veriga
#------------------------------------------
#začetna stran
# @get('/')
# def hello():
#     return template('prijava.html')

# @get('/hotelska_veriga')
# def hotelska_veriga():
#     # uporabnik = preveriUporabnika()
#     # if uporabnik is None: 
#     #     return
#     # napaka = nastaviSporocilo()
#     cur = baza.cursor()
#     hotelska_veriga = cur.execute("""
#         SELECT hotelska_veriga_id, ime_hotelske_verige, naslov_glavne_pisarne, spletna_stran, email_hotelske_verige FROM oseba
#         INNER JOIN posta ON posta.postna_st = oseba.naslov_id 
#         ORDER BY oseba.priimek
#     """) # napisali smo poizvedbo, kot seznam vrstic zelimo poslati v tamlete ki bi ga izrisal v tabelo
#     return template('hotelska_veriga.html', hotelska_veriga=hotelska_veriga)#, napaka=napaka)

# @post('/gostje/brisi/<gostje_id>')
# def brisi_gosta(gostje_id):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     cur = baza.cursor()
#     try:
#         cur.execute("DELETE FROM gostje WHERE gostje_id = ?", (gostje_id, ))
#     except:
#         nastaviSporocilo('Brisanje osebe z gostje_id {0} ni bilo uspešno.'.format(gostje_id)) 
#     redirect('/gostje')

# @get('/gostje/dodaj')
# def dodaj_gosta_get():
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     poste = cur.execute("SELECT posta FROM naslov")
#     return template('gost_edit.html', poste=poste, naslov="Dodaj gosta")

# @post('/gostje/dodaj') 
# def dodaj_gosta_post():
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     gostje_id = request.forms.gostje_id
#     ime = request.forms.ime
#     priimek = request.forms.priimek
#     email = request.forms.email
#     telefonska_stevilka = request.forms.telefonska_stevilka
#     naslov_id = request.forms.naslov_id
#     cur = baza.cursor()
#     cur.execute("INSERT INTO gostje (gostje_id,ime,priimek,telefonska_stevilka,email,kreditna_kartica,naslov_id) VALUES (?, ?, ?, ?, ?, ?)", 
#          (gostje_id,ime,priimek,telefonska_stevilka,email,kreditna_kartica,naslov_id))
#     redirect('/gostje')


# @get('/gostje/uredi/<gostje_id>')
# def uredi_gosta_get(gostje_id):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     cur = baza.cursor()
#     gost = cur.execute("SELECT gostje_id,ime,priimek,telefonska_stevilka,email,kreditna_kartica,naslov_id FROM gostje WHERE gostje_id = ?", (gostje_id,)).fetchone()
#     poste = cur.execute("SELECT postna_st, posta FROM posta")
#     return template('gost_edit.html', gost=gost, poste=poste, naslov="Uredi gosta")

# @post('/gostje/uredi/<gostje_id>')
# def uredi_gosta_post(gostje_id):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     novi_gostje_id = request.forms.gostje_id
#     ime = request.forms.ime
#     priimek = request.forms.priimek
#     email = request.forms.email
#     telefonska_stevilka = request.forms.telefonska_stevilka
#     kreditna_kartica = request.forms.kreditna_kartica
#     cur = baza.cursor()
#     cur.execute("UPDATE oseba SET gostje_id = ?, ime = ?, priimek = ?, email = ?, telefonska_stevilka = ?, naslov_id = ? WHERE gostje_id = ?", 
#          (novi_gostje_id, ime, priimek, email, telefonska_stevilka, naslov_id, gostje_id))
#     redirect('/gostje')

# ############################################
# ### Posta
# ############################################

# @get('/poste')
# def poste():
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     napaka = nastaviSporocilo()
#     cur = baza.cursor()
#     poste = cur.execute("""
#         SELECT postna_st, posta FROM posta
#     """)
#     return template('poste.html', poste=poste, napaka=napaka)

# @get('/poste/dodaj')
# def dodaj_posto_get():
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     return template('posta-edit.html')

# @post('/poste/dodaj') 
# def dodaj_posto():
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     postna_st = request.forms.postna_st
#     posta = request.forms.posta
#     cur = baza.cursor()
#     cur.execute("INSERT INTO posta (postna_st, posta) VALUES (?, ?)", (postna_st, posta))
#     redirect('/poste')

# @post('/poste/brisi/<postna_st>') 
# def brisi_posto(postna_st):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     cur = baza.cursor()
#     try:
#         cur.execute("DELETE FROM posta WHERE postna_st = ?", (postna_st, ))
#     except:
#         nastaviSporocilo('Brisanje pošte {0} ni bilo uspešno.'.format(postna_st)) 
#     redirect('/poste')

# @get('/poste/uredi/<postna_st>')
# def uredi_posto_get(postna_st):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     cur = baza.cursor()
#     posta = cur.execute("SELECT postna_st, posta FROM posta WHERE postna_st = ?", (postna_st,)).fetchone()
#     return template('posta-edit.html', posta=posta)

# @post('/poste/uredi/<postna_st>')
# def uredi_posto_post(postna_st):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     posta = request.forms.posta
#     cur = baza.cursor()
#     cur.execute("UPDATE posta SET posta = ? WHERE postna_st = ?", (posta, postna_st))
#     redirect('/poste')


# ############################################
# ### Račun
# ############################################

# @get('/gostje/<gostje_id>/racuni')
# def racuni_gosta(gostje_id):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     napaka = nastaviSporocilo()
#     cur = baza.cursor()
#     racuni = cur.execute("""
#         SELECT oseba.ime, oseba.priimek, racun.racun FROM racun 
#         INNER JOIN oseba ON oseba.gostje_id = racun.lastnik_id
#         WHERE oseba.gostje_id = ?
#     """, (gostje_id, )).fetchall()
#     if len(racuni) == 0:
#         nastaviSporocilo('gost še nima računa.') 
#         redirect('/gostje')
#         return
#     ime = racuni[0][0]
#     priimek = racuni[0][1]
#     return template('racuni.html', racuni=racuni, ime=ime, priimek=priimek, gostje_id=gostje_id, napaka=napaka)

# @get('/gostje/<gostje_id>/racuni/dodaj')
# def dodaj_racun_gosta(gostje_id):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     cur = baza.cursor()
#     cur.execute("INSERT INTO racun (lastnik_id) VALUES (?)", (gostje_id, ))
#     redirect('/gostje/{0}/racuni'.format(gostje_id))

# @post('/gostje/<gostje_id>/racuni/<racun>/brisi')
# def brisi_racun_gosta(gostje_id, racun):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return    
#     try:
#         cur.execute("DELETE FROM racun WHERE racun = ?", (racun, ))
#     except:
#         nastaviSporocilo('Brisanje računa številka {0} ni bilo uspešno.'.format(racun)) 
#     redirect('/gostje/{0}/racuni'.format(gostje_id))


# ############################################
# ### Transakcija
# ############################################

# @get('/gostje/<gostje_id>/racuni/<racun>/transakcije')
# def transakcije_gosta_na_racunu(gostje_id, racun):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return    
#     napaka = nastaviSporocilo()
#     cur = baza.cursor()
#     transakcije = cur.execute("SELECT id, datum, znesek FROM transakcija WHERE racun_id = ?", (racun, )).fetchall()
#     stanje = cur.execute("SELECT sum(znesek) FROM transakcija WHERE racun_id = ?", (racun, )).fetchone()
#     oseba = cur.execute("SELECT ime, priimek FROM oseba WHERE gostje_id = ?", (gostje_id, )).fetchone()
#     ime = oseba[0]
#     priimek = oseba[1]
#     return template('transakcije.html', transakcije=transakcije, ime=ime, priimek=priimek, racun=racun,
#        stanje=stanje[0], gostje_id=gostje_id, napaka=napaka)

# @get('/gostje/<gostje_id>/racuni/<racun>/transakcije/dodaj')
# def dodaj_transakcijo_na_racuni_gosta_get(gostje_id, racun):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     oseba = cur.execute("SELECT ime, priimek FROM oseba WHERE gostje_id = ?", (gostje_id, )).fetchone()
#     ime = oseba[0]
#     priimek = oseba[1]
#     stanje = cur.execute("SELECT sum(znesek) FROM transakcija WHERE racun_id = ?", (racun, )).fetchone()
#     return template('transakcija-edit.html', ime=ime, priimek=priimek, gostje_id=gostje_id, racun=racun, stanje=stanje[0])

# @post('/gostje/<gostje_id>/racuni/<racun>/transakcije/dodaj')
# def dodaj_transakcijo_na_racuni_gosta_post(gostje_id, racun):
#     uporabnik = preveriUporabnika()
#     if uporabnik is None: 
#         return
#     znesek = request.forms.znesek
#     cur = baza.cursor()
#     cur.execute("INSERT INTO transakcija (racun_id, znesek) VALUES (?, ?)", (racun, znesek))
#     redirect('/gostje/{0}/racuni/{1}/transakcije'.format(gostje_id, racun))
    

# ############################################
# ### Registracija, prijava
# ############################################

# def hashGesla(s):
#     m = hashlib.sha256()
#     m.update(s.encode("utf-8"))
#     return m.hexdigest()

@get('/registracija')
def registracija_get():
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka)

@post('/registracija')
def registracija_post():
    gostje_id = request.forms.gostje_id
    username = request.forms.username
    password = request.forms.password
    password2 = request.forms.password2
    if gostje_id is None or username is None or password is None or password2 is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    cur = baza.cursor()    
    uporabnik = None
    try: 
        uporabnik = cur.execute("SELECT * FROM oseba WHERE gostje_id = ?", (gostje_id, )).fetchone()
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
    cur.execute("UPDATE oseba SET username = ?, password = ? WHERE gostje_id = ?", (username, zgostitev, gostje_id))
    response.set_cookie('username', username, secret=skrivnost)
    redirect('/gostje')

# @get('/prijava')
# def prijava_get():
#     napaka = nastaviSporocilo()
#     return template('prijava.html', napaka=napaka)

# @post('/prijava')
# def prijava_post():
#     username = request.forms.username
#     password = request.forms.password
#     if username is None or password is None:
#         nastaviSporocilo('Uporabniško ima in geslo morata biti neprazna') 
#         redirect('/prijava')
#         return
#     cur = baza.cursor()    
#     hashBaza = None
#     try: 
#         hashBaza = cur.execute("SELECT password FROM oseba WHERE username = ?", (username, )).fetchone()
#         hashBaza = hashBaza[0]
#     except:
#         hashBaza = None
#     if hashBaza is None:
#         nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
#         redirect('/prijava')
#         return
#     if hashGesla(password) != hashBaza:
#         nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
#         redirect('/prijava')
#         return
#     response.set_cookie('username', username, secret=skrivnost)
#     redirect('/gostje')
    
# @get('/odjava')
# def odjava_get():
#     response.delete_cookie('username')
#     redirect('/prijava')

#-------------------------------------------------------------------------------------
# PRIKLOP NA BAZO
#-------------------------------------------------------------------------------------
baza = sqlite3.connect(baza_datoteka, isolation_level=None)

# radi bi videli kakšne sql stavke pošiljamo. To nam pomaga pri debuging.
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)

# zapoved upoštevanja omejitev FOREIGN KEY, da zares opošteva
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# Postavimo strežnik - reloader=True nam olajša razvoj (ozveževanje sproti - razvoj), da ni treba vsakič z nova treba zaganjati
run(host='localhost', port=8080, reloader=True)