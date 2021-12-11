import json
from pyproj import Transformer
from math import sqrt
import statistics
import sys

with open("adresy.geojson", encoding="utf-8") as a:
    adresy=json.load(a)

with open("kontejnery.geojson", encoding="utf-8") as k:
    kontejnery=json.load(k)

wgs2jtsk = Transformer.from_crs(4326,5514)
vzdalenosti_min={}
vzdalenost=None


for i in range (len(adresy['features'])):
    ulice_cislo=f"{adresy['features'][i]['properties']['addr:street']} {adresy['features'][i]['properties']['addr:housenumber']}"
    adresa_x=adresy['features'][i]['geometry']['coordinates'][1]
    adresa_y=adresy['features'][i]['geometry']['coordinates'][0]
    souradnice_krovak=wgs2jtsk.transform(adresa_x,adresa_y)
    vzdalenosti_min[ulice_cislo]=None
    for j in range (len(kontejnery['features'])):
        adresa_kontejneru=str(kontejnery['features'][j]['properties']['STATIONNAME'])
        kontejner_x,kontejner_y=kontejnery['features'][j]['geometry']['coordinates']
        vzdalenost=sqrt((souradnice_krovak[0]-kontejner_x)**2+(souradnice_krovak[1]-kontejner_y)**2)
        if kontejnery['features'][j]['properties']['PRISTUP']=="obyvatelům domu" and ulice_cislo==adresa_kontejneru:
            vzdalenosti_min[ulice_cislo]=0
        elif kontejnery['features'][j]['properties']['PRISTUP']=="volně":
            if vzdalenosti_min[ulice_cislo]==None or vzdalenosti_min[ulice_cislo]>vzdalenost:
                vzdalenosti_min[ulice_cislo]=vzdalenost
    if vzdalenosti_min[ulice_cislo]>10000:
        print("příliš velká vzdálenost k nejblišímu kontejneru")
        sys.exit()

     

maximum=0
maximum_s_adresou={}
median=statistics.median(vzdalenosti_min.values())
prumer=statistics.mean(vzdalenosti_min.values())
for a,d in vzdalenosti_min.items():
    if maximum<d:
        maximum=d
        maximum_s_adresou={a:d}


print(prumer)
print(maximum_s_adresou)
print(median)
print(i,j)

