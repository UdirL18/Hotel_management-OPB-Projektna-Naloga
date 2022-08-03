# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE hotelske_storitve
    (
    hotelske_storitve_id INT PRIMARY KEY NOT NULL,
    naziv_storitve varchar(45) NOT NULL,
    cena_storitve DECIMAL(10,2) NOT NULL,
    opis_storitve varchar(100),
    hotel_id INT REFERENCES hotel_podatki(hotel_id) NOT NULL
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE hotelske_storitve;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/hotelske_storitve.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO hotelske_storitve
                (hotelske_storitve_id,naziv_storitve,opis_storitve,cena_storitve,hotel_id)
                VALUES (%s, %s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 