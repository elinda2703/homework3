import json
import requests
from pyproj import Transformer
from math import sqrt
wgs2jtsk= Transformer.from_crs(4326,5514)

with open("adresy.geojson", encoding="utf-8") as a:
    adresy=json.load(a)

with open("kontejnery.geojson", encoding="utf-8") as k:
    kontejnery=json.load(k)


vzdalenosti_min={}
vzdalenost=None


for i in range (len(adresy['features'])):
    ulice_cislo=adresy['features'][i]['properties']['addr:street'],adresy['features'][i]['properties']['addr:housenumber']
    adresa_x=adresy['features'][i]['geometry']['coordinates'][1]
    adresa_y=adresy['features'][i]['geometry']['coordinates'][0]
    souradnice_krovak=wgs2jtsk.transform(adresa_x,adresa_y)
    vzdalenosti_min[ulice_cislo]=None
    print(souradnice_krovak)
    for j in range (len(kontejnery['features'])):
        
        kontejner_x=kontejnery['features'][j]['geometry']['coordinates'][0]
        kontejner_y=kontejnery['features'][j]['geometry']['coordinates'][1]
        vzdalenost=sqrt(((souradnice_krovak)[0]-kontejner_x)**2+(souradnice_krovak[1]-kontejner_y)**2)
        if kontejnery['features'][j]['properties']['PRISTUP']=="volně":
            if vzdalenosti_min[ulice_cislo]==None or vzdalenosti_min[ulice_cislo]>vzdalenost:
                vzdalenosti_min[ulice_cislo]=vzdalenost



#print(vzdalenosti_min)