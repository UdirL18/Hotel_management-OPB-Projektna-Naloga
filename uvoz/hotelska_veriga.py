# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE hotelska_veriga
    (
    hotelska_veriga_id INT PRIMARY KEY,
    ime_hotelske_verige varchar(45) NOT NULL,
    naslov_glavne_pisarne INT REFERENCES naslov(naslov_id) NOT NULL,
    spletna_stran varchar(45),
    email_hotelske_verige varchar(45) NOT NULL
    );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE hotelska_veriga;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/hotelska_veriga.csv", encoding="UTF-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO hotelska_veriga
                (hotelska_veriga_id, ime_hotelske_verige, naslov_glavne_pisarne, email_hotelske_verige, spletna_stran)
                VALUES (%s, %s, %s, %s, %s)
            """, r)
            #print("Uvožena hotelska_veriga %s" % (r[1], r[2], r[3], r[4], r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 