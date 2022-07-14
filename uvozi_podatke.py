import sqlite3
import os
import csv


baza_datoteka = 'HotelManagement.db'

#priklopiti se moram na bazo

def uvoziSQL(cur, datoteka):
   with open(datoteka) as f:
       koda = f.read()
       cur.executescript(koda)

#------------------------------------------
# Uvoz s SQL skript
#-----------------------------------------
# with sqlite3.connect(baza_datoteka) as baza:
#    cur = baza.cursor()
#    uvoziSQL(cur, 'Hotel.sql')
#    uvoziSQL(cur, 'Podatki/ocena.sql')
#    uvoziSQL(cur, 'Podatki/naslov.sql')
#    uvoziSQL(cur, 'Podatki/hotelska_veriga.sql')
#    uvoziSQL(cur, 'Podatki/hotel_podatki.sql')   
# #   uvoziSQL(cur, 'Podatki/gostje.sql')
# #   uvoziSQL(cur, 'Podatki/hotelska_veriga.sql')
# #   uvoziSQL(cur, 'Podatki/oddelek.sql')
# #   uvoziSQL(cur, 'Podatki/popusti_za_sobo.sql')
# #   uvoziSQL(cur, 'Podatki/rezervacije.sql')
# #   uvoziSQL(cur, 'Podatki/rezervirane_sobe.sql')
# #   uvoziSQL(cur, 'Podatki/soba.sql')
# #   uvoziSQL(cur, 'Podatki/tip_sobe.sql')
# #   uvoziSQL(cur, 'Podatki/uporabljene_storitve.sql')
# #   uvoziSQL(cur, 'Podatki/zaposleni.sql')
# #   uvoziSQL(cur, 'Podatki/hotelska_storitev.sql')

#   # with open('Hotel.sql') as f:
#   #   skript = f.read()
#   #   #print(skript)
#   # c.executescript(skript)


   
def uvoziCSV(cur, tabela):
   with open('Podatki/{0}.csv'.format(tabela)) as csvfile:
      podatki = csv.reader(csvfile)
      vsiPodatki = [vrstica for vrstica in podatki]
      glava = vsiPodatki[0]
      vrstice = vsiPodatki[1:]
      cur.executemany("INSERT INTO {0} ({1}) VALUES ({2})".format(
         tabela, ",".join(glava), ",".join(['?']*len(glava))), vrstice)

with sqlite3.connect(baza_datoteka) as baza:
   cur = baza.cursor()
   uvoziSQL(cur, 'Hotel.sql')
   uvoziCSV(cur, 'ocena')
   uvoziCSV(cur, 'naslov')
   uvoziCSV(cur, 'oddelek')
   uvoziCSV(cur, 'hotelska_veriga')
   uvoziCSV(cur, 'hotel_podatki')   
   uvoziCSV(cur, 'gostje')
   uvoziCSV(cur, 'zaposleni')
   uvoziCSV(cur, 'rezervacije')
   uvoziCSV(cur, 'hotelske_storitve')
   uvoziCSV(cur, 'uporabljene_storitve')  
   uvoziCSV(cur, 'popusti_za_sobo')
   uvoziCSV(cur, 'rezervirane_sobe')
   uvoziCSV(cur, 'sobe')
   uvoziCSV(cur, 'tipi_sob')
