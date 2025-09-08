from fastapi import FastAPI
import json

app = FastAPI()

with open("data/sale.json") as f:
    data = json.load(f)

@app.get("/pricesorted")
def price_sorted():
    sorteddata = sorted(data, key = lambda x: x['price'])
    return sorteddata