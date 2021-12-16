import json
from pyproj import Transformer
from math import sqrt
import statistics
import sys
from geojson import dump

try:
    with open("adresy.geojson", encoding="utf-8") as a:
        adresy = json.load(a)

    with open("kontejnery.geojson", encoding="utf-8") as k:
        kontejnery = json.load(k)
except FileNotFoundError:
    sys.exit("chybná vstupní data nebo špatný adresář")

def pythagorova_veta (x1, x2, y1, y2):
    prepona = sqrt((x1-x2)**2+(y1-y2)**2)
    return prepona
        
wgs2jtsk = Transformer.from_crs(4326, 5514, always_xy = True)
vzdalenosti_min = {}
adresy_kontejnery={}
vzdalenost = None
maximum = 0
adresa_maxima = None
for i in range(len(adresy['features'])):
    ulice_cislo = f"{adresy['features'][i]['properties']['addr:street']} {adresy['features'][i]['properties']['addr:housenumber']}"
    adresa_x, adresa_y = adresy['features'][i]['geometry']['coordinates']
    krovak_x, krovak_y = wgs2jtsk.transform(adresa_x, adresa_y)
    vzdalenosti_min[ulice_cislo] = float('inf')

    for j in range(len(kontejnery['features'])):
        id_kontejneru=kontejnery['features'][j]['properties']['ID']
        adresa_kontejneru = str(
            kontejnery['features'][j]['properties']['STATIONNAME'])
        kontejner_x, kontejner_y = kontejnery['features'][j]['geometry']['coordinates']
        if kontejnery['features'][j]['properties']['PRISTUP'] == "obyvatelům domu" and ulice_cislo == adresa_kontejneru:
            vzdalenosti_min[ulice_cislo] = 0  
            adresy['features'][i]['properties']['id_nejblizsiho_kontejneru']=id_kontejneru
        if kontejnery['features'][j]['properties']['PRISTUP'] == "volně":
            vzdalenost=pythagorova_veta(kontejner_x,krovak_x,kontejner_y,krovak_y)
            if vzdalenosti_min[ulice_cislo] > vzdalenost:
                vzdalenosti_min[ulice_cislo] = vzdalenost
                adresy_kontejnery[ulice_cislo]=id_kontejneru
                adresy['features'][i]['properties']['kontejner']=id_kontejneru

if vzdalenosti_min[ulice_cislo] > 10000:
    sys.exit("podezřele velké vzdálenosti k nejbližším kontejnerům")
        
median = int(round(statistics.median(vzdalenosti_min.values()),0))
prumer = int(round(statistics.mean(vzdalenosti_min.values()), 0))
for a, d in vzdalenosti_min.items():
    if maximum < d:
        maximum = d
        adresa_maxima = str(a)
print(f"Průměrná vzdálenost k nejbližšímu kontejneru je {prumer} m.")
print(f"Nejdále je to ke kontejneru z adresy {adresa_maxima} a to {int(round(maximum))} m.")
print(f"Medián vzdáleností je {median} m.")
with open('adresy_kontejnery.geojson', 'w', encoding="utf-8") as f:
    dump(adresy, f, ensure_ascii=False, indent=4)