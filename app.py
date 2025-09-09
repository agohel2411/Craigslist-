from fastapi import FastAPI
import json
import math
from src import model
from sqlalchemy.orm import Session
from fastapi import Depends,status
from src.model import Sales
from src.database import SessionLocal, engine
from fastapi import HTTPException
from sqlalchemy import desc, or_, and_
from src.log import logger

model.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def get_db():
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

## JSON File Handeling

with open("data/sale.json") as f:
    data = json.load(f)

logger.info(f"API Loaded")

@app.get("/getsorteddata", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def price_sorted(reverse: bool, criteria: str):
    logger.info(f"Hitted /getsorteddata (json): reverse = {reverse}, criteria = {criteria}")
    try:
        sorteddata = sorted(data, key=lambda x: x[criteria], reverse=reverse)

        if sorteddata:
            logger.info(f"Successfully returned {'reversed' if reverse else ''} sorted data by {criteria} in /getsorteddata (json)")
            return sorteddata
        else:
            logger.error(f"Error Raised in /getsorteddata: 404 - No data found (josn)")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")

    except KeyError:
        logger.error(f"Criteria provided ({criteria}) in /getsorteddata was invalid (json)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort criteria: '{criteria}'")

    except Exception as e:
        logger.error(f"Error raised in /getsorteddata: {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/getitem", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def singleitem(id: str | None = None, long: float | None = None, lat: float | None = None):
    logger.info(f"Hitted /getitem (json): {f'id = {id}' if id  else f'lattitude = {lat}, longitude = {long}'}")
    try:
        if (not id) or (not lat) or (not long):
            logger.error("Any parameter not provided in /getitem (josn)")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid criteria: Provide any one parameter to proceed")
        
        logger.info(f"Successfully returned data containing {'id' if id else 'location'} in /getitem (json)")
        return [person for person in data if ((person['id']==id) or (person['loc']==[long,lat]))]
    except Exception as e:
        logger.error(f"Error raised in /getitem: {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/getitemlist", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def listitem(status: str | None = None, userid: str | None = None):
    logger.info(f"Hitted /getitemlist (json): {f'status = {status}' if status else f'criteria = {userid}'}")
    try:
        if (not status) or (not userid):
            logger.error("Any parameter not provided in /getitemlist")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Criteria: Provide any one parameter (status -- or -- userid) to proceed")
        
        logger.info(f"Successfully returned data of having {status} status and {userid} userId in /getitemlist (josn)")
        return [person for person in data if ((person['status']==status) or (person['userId']==userid) if status or userid else (person['status']==status) and (person['iserId']==userid))]
    except Exception as e:
        logger.error(f"Error raised in /getitemlist: {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/get_items_in_radius", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def radius(radius: float, latitude: float, longitude: float):
    logger.info(f"Hitted /get_items_in_radius (json): radius = {radius}, latitude = {latitude}, longitude = {longitude}")
    try:
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
        logger.info(f"Successfully returned datapoints within radius of {radius}km from location [{latitude},{longitude}] in /get_item_in_radius (json)")
        return len(lst)
    except Exception as e:
        logger.error(f"Error raised in /get_item_by_radius: {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/get_items_by_filter", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def multifilter(filterby: str, upper: int | None = None, lower: int | None = None, words: str | None = None, radius: float | None = None, latitude: float | None = None, longitude: float | None = None):

    try:    
        if filterby == 'price':
            logger.info(f"Hitted /get_items_by_filter (json): filter = {filterby}, upper = {upper}, lower = {lower}")
            if lower>upper:
                logger.error(f"Upper value {upper} less than lower value {lower} in /get_items_by_filter (json)")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid parameters: Upper value cannot be less than lower")
            
            logger.info(f"Successfully data returned having prices from {lower} to {upper} in /get_items_by_filter (json)")
            return [person for person in data if ((person[filter]>lower) and (person[filter]<upper))]
        
        elif filterby == 'desc':
            logger.info(f"Hitted /get_items_by_filter (json): filter = {filterby}, words = {words}")
            for person in data:
                if person['description'] != None:
                    if words in person['description']:
                        logger.info(f"Successfully returned data containing {words} in description from /get_items_by_filter (json)")
                        return person
        elif filterby == 'radius':
            logger.info(f"Hitted /get_items_by_filter (json): filter = {filterby}, radius = {upper}, lower = {lower}")
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

            logger.info(f"Successfully returned datapoints within radius of {radius}km from location [{latitude},{longitude}] in /get_items_by_filter (json)")
            return lst
        else:
            logger.error(f"Invalid filter value ({filterby}) provided in /get_items_by_filter (json)")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Parameter: Please provide valid filter")
    except Exception as e:
        logger.error(f"Error raised in /get_items_by_filter: {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        

## SQL File Handeling

@app.get("/getsorteddatadb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def pricesorted(reverse: bool, criteria: str, db: Session = Depends(get_db)):
    try:
        column = getattr(Sales, criteria)
        order = desc(column) if reverse else column
        sorteddata = db.query(Sales).order_by(order).all()
        if sorteddata:
            return sorteddata
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort criteria: {criteria}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/getitemdb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def singleitem(id: str | None = None, lat: float | None = None, long: float | None = None, db: Session = Depends(get_db)):
    try:
        if (not id) or (not lat) or (not long):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid criteria: Provide any one parameter to proceed")
        blog = db.query(Sales).filter(or_(Sales.id==id, and_(Sales.lat==lat, Sales.long==long))).all()
        return blog
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/getitemistdb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def listitemdb(status: str | None = None, userid: str | None = None, db: Session = Depends(get_db)):
    try:
        blog = db.query(Sales).filter(or_(Sales.status==status, Sales.userId==userid)).all()
        if (not status) and (not userid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Criteria: Provide any one parameter (status -- or -- userid) to proceed")
        return blog
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@app.get("/get_items_in_radiusdb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def radiusdb(radius: float, latitude: float, longitude: float, db: Session = Depends(get_db)):
    try:    
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/multifilterdb", tags=['SQL Db'])
def multifilterdb(filter: str, upper: int | None = None, lower: int | None = None, words: str | None = None, radius: float | None = None, latitude: float | None = None, longitude: float | None = None, db: Session = Depends(get_db)):
    try:
        if filter == 'price':
            if lower>upper:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid parameters: Upper value cannot be less than lower")
            
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
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Parameter: Please provide valid filter")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        