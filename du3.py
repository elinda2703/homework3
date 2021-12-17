import json
from pyproj import Transformer
from math import sqrt, inf
import statistics
import sys
from geojson import dump
# načte data ze souborů s adresními body a kontejnery, spadne, když nemůže soubor najít nebo ho program nemá právo číst
try:
    with open("adresy.geojson", encoding="utf-8") as a:
        adresy = json.load(a)

    with open("kontejnery.geojson", encoding="utf-8") as klic:
        kontejnery = json.load(klic)
except FileNotFoundError:
    sys.exit("chybná vstupní data nebo špatný adresář")
except PermissionError:
    sys.exit("program nemá právo číst vstupní soubor")

# spočítá délku přepony pravoúhlého trojúhelníku při zadaných souřadnicích koncových bodů této přepony


def pythagorova_veta(x1, x2, y1, y2):
    prepona = sqrt((x1-x2)**2+(y1-y2)**2)
    return prepona


# převede WGS souřadnice na S-JTSK souřadnice
wgs2jtsk = Transformer.from_crs(4326, 5514, always_xy=True)
# do tohoto slovníku se budou ukládat adresy (klíč) a vzdálenost k nejbližšímu kontejneru (hodnota)
vzdalenosti_min = {}
# sem se bude ukládat id adresy (klíč) a jemu příslušné ID nejbližšího kontejneru (hodnota)
adresa_id_kontejneru = {}

MAX_VZDALENOST = 10000  # maximální vzdálenost nejbližšího kontejneru


# získá potřebné informace ze souboru s adresami
def parse_addresa(adresa):
    ulice_cislo = f"{adresa['properties']['addr:street']} {adresa['properties']['addr:housenumber']}"
    adresa_x, adresa_y = adresa['geometry']['coordinates']
    id_adresy = adresa['properties']['@id']
    return adresa_x, adresa_y, ulice_cislo, id_adresy

# získá potřebné informace ze souboru s kontejnery


def parse_kontejner(kontejner):
    id_kontejneru = kontejner['properties']['ID']
    adresa_kontejneru = str(
        kontejner['properties']['STATIONNAME'])
    kontejner_x, kontejner_y = kontejner['geometry']['coordinates']
    pristup = kontejner['properties']['PRISTUP']
    return adresa_kontejneru, id_kontejneru, kontejner_x, kontejner_y, pristup


# uloží potřebné informace o adresách do seznamu n-tic
parsovane_adresy = [parse_addresa(x) for x in adresy['features']]
# uloží potřebné informace o kontejnerech do seznamu n-tic
parsovane_kontejnery = [parse_kontejner(x) for x in kontejnery['features']]

# v tomto cyklu se převedou sořadnice adresních bodů do S-JTSK a vzdálenost k nejbližšímu kontejneru je inicializovůna jako nekonečno
for adresa_x, adresa_y, ulice_cislo, id_adresy in parsovane_adresy:
    krovak_x, krovak_y = wgs2jtsk.transform(adresa_x, adresa_y)
    vzdalenosti_min[ulice_cislo] = inf
    # v tomto cyklu se adresám s privátním kontejnerem (pristup == "obyvatelům domu") přiřadí nulová vzdálenost k nejbližšímu kontejneru a těm ostatním se přiřadí nejmenší vypočítaná vzdálenost ke kontejneru

    for adresa_kontejneru, id_kontejneru, kontejner_x, kontejner_y, pristup in parsovane_kontejnery:
        if pristup == "obyvatelům domu" and ulice_cislo == adresa_kontejneru:
            vzdalenosti_min[ulice_cislo] = 0

            adresa_id_kontejneru[id_adresy] = id_kontejneru
        if pristup == "volně":
            vzdalenost = pythagorova_veta(
                kontejner_x, krovak_x, kontejner_y, krovak_y)
            if vzdalenosti_min[ulice_cislo] > vzdalenost:
                vzdalenosti_min[ulice_cislo] = vzdalenost

                adresa_id_kontejneru[id_adresy] = id_kontejneru
    # program spadne, když jsou vzdálenosti k nejbližším kontejnerů příliš velké
    if vzdalenosti_min[ulice_cislo] > MAX_VZDALENOST:
        sys.exit("podezřele velké vzdálenosti k nejbližším kontejnerům")

# výpočet mediánu vzdáleností k nejbližšímu kontejneru
median = round(statistics.median(vzdalenosti_min.values()))
# výpočet průměru vzdáleností k nejbližšímu kontejneru
prumer = round(statistics.mean(vzdalenosti_min.values()))

# přidá id nejbližšího kontejneru k původním datům s adresami
for adresa in adresy['features']:
    for klic, hodnota in adresa_id_kontejneru.items():
        if klic == adresa['properties']['@id']:
            adresa['properties']['kontejner'] = hodnota

maximum = -inf
# získání největší vzdálenosti k nejbližšímu kontejneru
for a, d in vzdalenosti_min.items():
    if maximum < d:
        maximum = d
        adresa_maxima = str(a)

# výpis
print(f"Průměrná vzdálenost k nejbližšímu kontejneru je {prumer} m.")
print(
    f"Nejdále je to ke kontejneru z adresy {adresa_maxima} a to {round(maximum)} m.")
print(f"Medián vzdáleností je {median} m.")

# vytvoří soubor s daty o adresách s přidaným id nejbližšího kontejneru
with open('adresy_kontejnery.geojson', 'w', encoding="utf-8") as f:
    dump(adresy, f, ensure_ascii=False, indent=4)
