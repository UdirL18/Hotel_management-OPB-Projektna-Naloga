# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE zaposleni
    (
    zaposleni_id SERIAL PRIMARY KEY NOT NULL,
    ime varchar(45) NOT NULL,
    priimek varchar(45) NOT NULL,
    naziv  varchar(45) NOT NULL,
    naslov_id INT REFERENCES Naslov(Naslov_id) NOT NULL,
    hotel_id INT REFERENCES hotel_podatki(Hotel_id) NOT NULL,
    oddelek_id INT REFERENCES Oddelek(Oddelek_id) NOT NULL,
    telefonska_stevilka  varchar(12) NOT NULL,
    email  varchar(45) NOT NULL
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE zaposleni;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/zaposleni.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO zaposleni
                (zaposleni_id,ime,priimek,naziv,telefonska_stevilka,email,oddelek_id,naslov_id,hotel_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 