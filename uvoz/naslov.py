# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE naslov
    (
    naslov_id INT PRIMARY KEY NOT NULL,
    mesto varchar(45) NOT NULL,
    drzava varchar(45) NOT NULL,
    posta varchar(45) NOT NULL
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE naslov;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/naslov.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO naslov
                (naslov_id, mesto, drzava, posta)
                VALUES (%s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 