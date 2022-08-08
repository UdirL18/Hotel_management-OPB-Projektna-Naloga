# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE popusti_za_sobo
    (
    popust_id SERIAL PRIMARY KEY NOT NULL,
    mesec_zacetka INT, 
    mesec_konca INT,
    diskontna_stopnja DECIMAL(10,2) NOT NULL,
    tip_sobe_id INT REFERENCES Tipi_sob(Tip_sobe_id)
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE popusti_za_sobo;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/popusti_za_sobo.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO popusti_za_sobo
                (popust_id,mesec_zacetka,mesec_konca,diskontna_stopnja,tip_sobe_id)
                VALUES (%s, %s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 