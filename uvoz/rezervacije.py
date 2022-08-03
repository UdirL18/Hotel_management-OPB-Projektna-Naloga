# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE rezervacije
    (
    rezervacije_id INT PRIMARY KEY NOT NULL,
    tip_placila varchar(45) NOT NULL,
    datum_rezervacije DATE NOT NULL,
    st_rezerviranih_sob INT NOT NULL,
    datum_check_in DATE NOT NULL,
    datum_check_out DATE NOT NULL,
    zaposleni_id INT REFERENCES zaposleni(zaposleni_id) NOT NULL, 
    gostje_id INT REFERENCES gostje(gostje_id) NOT NULL, 
    hotel_id INT REFERENCES hotel_podatki(hotel_id) NOT NULL
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE rezervacije;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/rezervacije.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO rezervacije
                (rezervacije_id,tip_placila,datum_rezervacije,st_rezerviranih_sob,datum_check_in,datum_check_out,zaposleni_id,gostje_id,hotel_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 