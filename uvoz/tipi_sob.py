# uvozimo ustrezne podatke za povezavo
from . import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE tipi_sob
    (
    tip_sobe_id INT PRIMARY KEY NOT NULL,
    tip_sobe_ime varchar(45) NOT NULL,
    tip_sobe_opis varchar(100),
    cena_sobe DECIMAL(10,2) NOT NULL,
    zivali INT, 
    kadilci INT
    );
    """) 
    conn.commit() #ko delam poizvedbe, da se potrdijo 

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE tipi_sob;
    """)
    conn.commit()

def uvozi_podatke():
    with open("Podatki/tipi_sob.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO tipi_sob
                (tip_sobe_id, tip_sobe_ime, tip_sobe_opis, cena_sobe, zivali, kadilci)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, r)
            #rid, = cur.fetchone()
            #print("Uvožen naslov %s" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 