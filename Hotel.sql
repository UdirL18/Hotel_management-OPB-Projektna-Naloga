DROP TABLE IF EXISTS hotelska_veriga;
DROP TABLE IF EXISTS hotel_podatki;
DROP TABLE IF EXISTS sobe;
DROP TABLE IF EXISTS tipi_sob;
DROP TABLE IF EXISTS rezervirane_sobe;
DROP TABLE IF EXISTS popusti_za_sobo;
DROP TABLE IF EXISTS rezervacije;
DROP TABLE IF EXISTS ocena;
DROP TABLE IF EXISTS uporabljene_storitve;
DROP TABLE IF EXISTS hotelske_storitve;
DROP TABLE IF EXISTS zaposleni;
DROP TABLE IF EXISTS oddelek;
DROP TABLE IF EXISTS gostje;
DROP TABLE IF EXISTS naslov;

CREATE TABLE hotelska_veriga
(
  hotelska_veriga_id INT PRIMARY KEY,
  ime_hotelske_verige varchar(45) NOT NULL,
  naslov_glavne_pisarne varchar(12) REFERENCES naslov(naslov_id) NOT NULL,
  spletna_stran varchar(45),
  email_hotelske_verige varchar(45) NOT NULL
);

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
  check_out TIME,
  check_in TIME,
  ocena INT REFERENCES ocena(ocena),
  hotelska_veriga_id INT REFERENCES hotelska_veriga(hotelska_veriga_id),
  naslov_id INT REFERENCES naslov(naslov_id)
);


CREATE TABLE sobe
(
	soba_ID INT PRIMARY KEY NOT NULL,
  stevilka_sobe INT(4) NOT NULL,
  tip_sobe_id INT REFERENCES Tipi_Sob(Tip_sobe_id),
  hotel_id INT REFERENCES hotel_podatki(Hotel_id) 
);


CREATE TABLE tipi_sob
(
	tip_sobe_id INT PRIMARY KEY NOT NULL,
  tip_sobe_ime varchar(45) NOT NULL,
  tip_sobe_opis varchar(100),
  cena_sobe DECIMAL(10,2) NOT NULL,
  zivali TINYINT(1), 
  kadilci TINYINT(1)
);

CREATE TABLE rezervacije
(
  rezervacije_id INT PRIMARY KEY NOT NULL,
  tip_placila varchar(45) NOT NULL,
  datum_rezervacije DATETIME NOT NULL,
  st_rezerviranih_sob INT NOT NULL,
  datum_check_in DATETIME NOT NULL,
  datum_check_out DATETIME NOT NULL,
  zaposleni_id INT REFERENCES zaposleni(zaposleni_id) NOT NULL, 
  gostje_id INT REFERENCES gostje(gostje_id) NOT NULL, 
  hotel_id INT REFERENCES hotel_podatki(hotel_id) NOT NULL
);

CREATE TABLE rezervirane_sobe
(
	rezervirane_sobe_id INT PRIMARY KEY NOT NULL,
	rezervacije_id INT REFERENCES rezervacije(rezervacije_id),
  sobe_id INT REFERENCES sobe(soba_id)
);



CREATE TABLE popusti_za_sobo
(
	popust_id INT PRIMARY KEY NOT NULL,
  mesec_zacetka TINYINT(2), 
  mesec_konca TINYINT(2),
  diskontna_stopnja DECIMAL(10,2) NOT NULL,
  tip_sobe_id INT REFERENCES Tipi_sob(Tip_sobe_id)
);





CREATE TABLE ocena
(
  ocena INT PRIMARY KEY NOT NULL
);


CREATE TABLE uporabljene_storitve
(
  uporabljene_storitve_id INT PRIMARY KEY NOT NULL,
  hotelske_storitve_id INT REFERENCES hotelske_storitve(hotelske_storitve_id) NOT NULL,
  rezervacije_id INT REFERENCES rezervacije(rezervacije_id) NOT NULL
);


CREATE TABLE hotelske_storitve
(
  storitve_id INT PRIMARY KEY NOT NULL,
  naziv_storitve varcher(45) NOT NULL,
  cena_storitve DECIMAL(10,2) NOT NULL,
  opis_storitve varcher(100),
  hotel_id INT REFERENCES hotel_podatki(Hotel_id) NOT NULL
);


CREATE TABLE zaposleni
(
	zaposleni_id INT PRIMARY KEY NOT NULL,
	ime varchar(45) NOT NULL,
	priimek varchar(45) NOT NULL,
	naziv  varchar(45) NOT NULL,
  naslov_id INT REFERENCES Naslov(Naslov_id) NOT NULL,
  hotel_id INT REFERENCES hotel_podatki(Hotel_id) NOT NULL,
  oddelek_id INT REFERENCES Oddelek(Oddelek_id) NOT NULL,
  telefonska_stevilka  varchar(12) NOT NULL,
  email  varchar(45) NOT NULL

);


CREATE TABLE oddelek
(
  oddelek_id INT PRIMARY KEY NOT NULL,
  oddelek_ime varchar(45) NOT NULL,
  oddelek_opis Varchar(100)    
);


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


CREATE TABLE naslov
(
  naslov_id INT PRIMARY KEY NOT NULL,
  mesto varchar(45) NOT NULL,
  drzava varchar(45) NOT NULL,
  posta varchar(6) NOT NULL
);