import json
from pyproj import Transformer
from math import sqrt
import statistics
import sys
try:
    with open("adresy.geojson", encoding="utf-8") as a:
        adresy = json.load(a)

    with open("kontejnery.geojson", encoding="utf-8") as k:
        kontejnery = json.load(k)

    wgs2jtsk = Transformer.from_crs(4326, 5514)
    vzdalenosti_min = {}
    vzdalenost = None
    for i in range(len(adresy['features'])):
        ulice_cislo = f"{adresy['features'][i]['properties']['addr:street']} {adresy['features'][i]['properties']['addr:housenumber']}"
        adresa_y, adresa_x = adresy['features'][i]['geometry']['coordinates']
        souradnice_krovak = wgs2jtsk.transform(adresa_x, adresa_y)
        vzdalenosti_min[ulice_cislo] = None
        for j in range(len(kontejnery['features'])):
            adresa_kontejneru = str(
                kontejnery['features'][j]['properties']['STATIONNAME'])
            kontejner_x, kontejner_y = kontejnery['features'][j]['geometry']['coordinates']
            vzdalenost = int(round(sqrt(
                (souradnice_krovak[0]-kontejner_x)**2+(souradnice_krovak[1]-kontejner_y)**2), 0))
            if kontejnery['features'][j]['properties']['PRISTUP'] == "obyvatelům domu" and ulice_cislo == adresa_kontejneru:
                vzdalenosti_min[ulice_cislo] = 0
            elif kontejnery['features'][j]['properties']['PRISTUP'] == "volně":
                if vzdalenosti_min[ulice_cislo] == None or vzdalenosti_min[ulice_cislo] > vzdalenost:
                    vzdalenosti_min[ulice_cislo] = vzdalenost
        if vzdalenosti_min[ulice_cislo] > 10000:
            print("příliš velká vzdálenost k nejblišímu kontejneru")
            sys.exit()

    maximum = 0
    adresa_maxima = None
    median = statistics.median(vzdalenosti_min.values())
    prumer = int(round(statistics.mean(vzdalenosti_min.values()), 0))
    for a, d in vzdalenosti_min.items():
        if maximum < d:
            maximum = d
            adresa_maxima = str(a)

    print(f"Průměrná vzdálenost k nejbližšímu kontejneru je {prumer} m.")
    print(f"Nejdále je to ke kontejneru z adresy {adresa_maxima} a to {maximum} m.")
    print(f"Medián vzdáleností je {median} m.")
    print(i, j)
except FileNotFoundError:
    print("chybná vstupní data")
