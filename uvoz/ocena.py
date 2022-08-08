# uvozimo ustrezne podatke za povezavo
from . import auth 

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE ocena
    (
    ocena SERIAL PRIMARY KEY NOT NULL
    );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE ocena;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/ocena.csv", encoding="UTF-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO ocena
                (ocena)
                VALUES (%s)
            """, r)
            print("Uvožena ocena %s" % (r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 