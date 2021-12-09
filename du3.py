import json
import requests
from pyproj import Transformer
wgs2jtsk= Transformer.from_crs(4326,5514)

with open("adresy.geojson", encoding="utf-8") as a:
    adresy=json.load(a)

with open("kontejnery.geojson", encoding="utf-8") as k:
    kontejnery=json.load(k)



souradnice_adresy=[]
for i in range(len(adresy['features'])):
    souradnice_adresy.append(adresy['features'][i]['geometry']['coordinates'])

adresy_krovak=wgs2jtsk.transform(souradnice_adresy[0][1],souradnice_adresy[0][0])
print(adresy_krovak)