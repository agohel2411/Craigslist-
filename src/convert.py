from database import engine, SessionLocal
import json
from model import Sales ## base model
import model

db = SessionLocal()

model.Base.metadata.create_all(bind=engine)

with open("./data/sale.json") as f:
    data = json.load(f)


try:
    db = SessionLocal()
    for person in data:
        new_data = Sales(
            id = person['id'],
            lat = person['loc'][0],
            long = person['loc'][1],
            userId = person['userId'],
            description = person['description'],
            price = person['price'],
            status = person['status']
        )
        db.add(new_data)
    db.commit()
    print("data added")
finally:
    db.close()