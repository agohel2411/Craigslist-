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