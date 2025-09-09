from fastapi import FastAPI
from typing import Optional
import json
import math
from src import schema, model
from sqlalchemy.orm import Session
from fastapi import Depends,status
from src.model import Sales
from src.database import Base, SessionLocal, engine
from fastapi import HTTPException

model.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def get_db():
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

with open("data/sale.json") as f:
    data = json.load(f)

@app.get("/getsorteddata", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def price_sorted(reverse: bool, criteria = str):
    try:
        sorteddata = sorted(data, key=lambda x: x[criteria], reverse=reverse)

        if sorteddata:
            return sorteddata
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")

    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort criteria: '{criteria}'")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/getitem", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def singleitem(id: str | None = None, long: float | None = None, lat: float | None = None):
    try:
        if (not id) and (not lat) and (not long):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid criteria: Provide any one parameter to proceed")
        
        return [person for person in data if ((person['id']==id) or (person['loc']==[long,lat]))]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/getitemlist", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def listitem(status: str | None = None, userid: str | None = None):
    try:
        if (not status) and (not userid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Criteria: Provide any one parameter (status -- or -- userid) to proceed")
        return [person for person in data if ((person['status']==status) or (person['userId']==userid))]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/get_items_by_filter", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def multifilter(filterby: str, upper: int | None = None, lower: int | None = None, words: str | None = None, radius: float | None = None, latitude: float | None = None, longitude: float | None = None):
    try:    
        if filterby == 'price':
            if lower>upper:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid parameters: Upper value cannot be less than lower")
            return [person for person in data if ((person[filter]>lower) and (person[filter]<upper))]
        elif filterby == 'desc':
            for person in data:
                if person['description'] != None:
                    if words in person['description']:
                        return person
        elif filterby == 'radius':
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

            return lst
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Parameter: Please provide valid filter")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@app.get("/radius", tags=['Json'])
def radius(radius: float, latitude: float, longitude: float):
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



@app.get("/pricesorteddb", tags=['SQL Db'])
def pricesorted(db: Session = Depends(get_db)):
    
    blog = db.query(Sales).order_by(Sales.price).all()
    return blog

from sqlalchemy import or_, and_

@app.get("/singleitemdb", tags=['SQL Db'])
def singleitem(id: str | None = None, lat: float | None = None, long: float | None = None, db: Session = Depends(get_db)):
    blog = db.query(Sales).filter(or_(Sales.id==id, and_(Sales.lat==lat, Sales.long==long))).all()
    return blog

@app.get("/listdb", tags=['SQL Db'])
def listitemdb(status: str | None = None, userId: str | None = None, db: Session = Depends(get_db)):
    blog = db.query(Sales).filter(or_(Sales.status==status, Sales.userId==userId)).all()
    return blog

@app.get("/radiusdb", tags=['SQL Db'])
def radiusdb(radius: float, latitude: float, longitude: float, db: Session = Depends(get_db)):
    R = 6371

    lat1_rad = math.radians(latitude)
    lon1_rad = math.radians(longitude)
    lst = []

    users = db.query(Sales).all()

    for user in users:
        lat2_rad = math.radians(user.lat)
        lon2_rad = math.radians(user.long)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c

        if distance<radius:
            lst.append(user)

    return [user.__dict__ for user in lst]

@app.get("/multifilterdb", tags=['SQL Db'])
def multifilterdb(filter: str, upper: int | None = None, lower: int | None = None, words: str | None = None, radius: float | None = None, latitude: float | None = None, longitude: float | None = None, db: Session = Depends(get_db)):
    if filter == 'price':
        blog = db.query(Sales).filter(and_(Sales.price>lower, Sales.price<upper)).all()
        return blog
    elif filter == 'desc':
        blog = db.query(Sales).filter(Sales.description.like(f'%{words}%')).all()
        return blog
    elif filter == 'radius':
        R = 6371

        lat1_rad = math.radians(latitude)
        lon1_rad = math.radians(longitude)
        lst = []

        users = db.query(Sales).all()

        for user in users:
            lat2_rad = math.radians(user.lat)
            lon2_rad = math.radians(user.long)

            dlon = lon2_rad - lon1_rad
            dlat = lat2_rad - lat1_rad

            # Haversine formula
            a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            distance = R * c

            if distance<radius:
                lst.append(user)

        return [user.__dict__ for user in lst]