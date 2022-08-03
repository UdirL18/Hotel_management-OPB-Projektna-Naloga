# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE hotel_podatki
    (
    hotel_id INT PRIMARY KEY, 
    ime_hotela varchar(45) NOT NULL,
    telefonska_stevilka varchar(12) NOT NULL,
    opis_hotela varchar(100),
    email varchar(45) NOT NULL,
    spletna_stran varchar(45),
    stevilo_lezisc INT,
    stevilo_nadstropij INT,
    check_out DATE,
    check_in DATE,
    ocena INT REFERENCES ocena(ocena),
    hotelska_veriga_id INT REFERENCES hotelska_veriga(hotelska_veriga_id),
    naslov_id INT REFERENCES naslov(naslov_id)
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE hotel_podatki;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/hotel_podatki.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO hotel_podatki
                (hotel_id,ime_hotela,naslov_id,telefonska_stevilka,email,spletna_stran,opis_hotela,stevilo_nadstropij,stevilo_lezisc,hotelska_veriga_id,ocena,check_in,check_out)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 