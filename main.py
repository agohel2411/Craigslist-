from fastapi import FastAPI
from typing import Optional
import json

app = FastAPI()

with open("data/sale.json") as f:
    data = json.load(f)

@app.get("/pricesorted")
def price_sorted():
    sorteddata = sorted(data, key = lambda x: x['price'])
    return sorteddata

@app.get("/singleitem")
def singleitem(id: str | None = None, long: float | None = None, lat: float | None = None):
    return [person for person in data if ((person['id']==id) or (person['loc']==[long,lat]))]

@app.get("/list")
def listitem(status: str | None = None, userId: str | None = None):
    return [person for person in data if ((person['status']==status) or (person['userId']==userId))]

import math
@app.get("/multifilter")
def multifilter(filter: str, upper: int | None = None, lower: int | None = None, words: str | None = None, radius: float | None = None, latitude: float | None = None, longitude: float | None = None):
    if filter == 'price':
        return [person for person in data if ((person[filter]>lower) and (person[filter]<upper))]
    elif filter == 'desc':
        for person in data:
            if person['description'] != None:
                if words in person['description']:
                    return person
    elif filter == 'radius':
        R = 6371

        lat1_rad = math.radians(latitude)
        lon1_rad = math.radians(longitude)
        lst = []

        for person in data:
            coordinates = person['loc']
            lat2_rad = math.radians(coordinates[0])
            lon2_rad = math.radians(coordinates[1])

            dlon = lon2_rad - lon1_rad
            dlat = lat2_rad - lat1_rad

            # Haversine formula
            a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            distance = R * c
            

            if distance<radius:
                lst.append(person)

        return len(lst)
        
        