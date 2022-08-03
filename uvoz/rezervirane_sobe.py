# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE rezervirane_sobe
    (
        rezervirane_sobe_id INT PRIMARY KEY NOT NULL,
        rezervacije_id INT REFERENCES rezervacije(rezervacije_id),
    sobe_id INT REFERENCES sobe(soba_id)
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE rezervirane_sobe;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/rezervirane_sobe.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO rezervirane_sobe
                (rezervirane_sobe_id,rezervacije_id,sobe_id)
                VALUES (%s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 