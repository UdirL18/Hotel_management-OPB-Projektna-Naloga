# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE gostje
    (
    gostje_id INT PRIMARY KEY NOT NULL,
    ime varchar(45) NOT NULL,
    priimek varchar(45) NOT NULL,
    kreditna_kartica varchar(45),
    email varchar(45) NOT NULL,
    telefonska_stevilka varchar(12) NOT NULL, 
    naslov_id INT REFERENCES Naslov(Naslov_id)
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE gostje;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/gostje.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO gostje
                (gostje_id,ime,priimek,telefonska_stevilka,email,kreditna_kartica,naslov_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)