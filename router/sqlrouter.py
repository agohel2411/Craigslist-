from fastapi import APIRouter
import math
from sqlalchemy.orm import Session
from fastapi import Depends,status
from src.model import Sales
from src.database import SessionLocal
from fastapi import HTTPException
from sqlalchemy import desc, or_, and_, func
from src.log import logger
import fastapi

router = APIRouter(tags=["SQL Db"])

db = SessionLocal()

def get_db():
    try:
        yield db
    finally:
        db.close()

@router.get("/getsorteddatadb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def pricesorted(reverse: bool, criteria: str, db: Session = Depends(get_db)):
    logger.info(f"Hitted /getsorteddatadb (sql): reverse = {reverse}, criteria = {criteria}")
    try:
        column = getattr(Sales, criteria)
        order = desc(column) if reverse else column
        sorteddata = db.query(Sales).order_by(order).all()
        if sorteddata:
            logger.info(f"Successfully returned {'reversed' if reverse else ''} sorted data by {criteria} in /getsorteddatadb (sql)")
            return sorteddata
        else:
            logger.error(f"Error Raised in /getsorteddatadb: 404 - No data found (sql)")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
    except AttributeError:
        logger.error(f"Criteria provided ({criteria}) in /getsorteddatadb was invalid (sql)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort criteria: {criteria}")
    except Exception as e:
        logger.error(f"Error raised in /getsorteddatadb: {str(e)} (sql)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/getitemdb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def singleitem(id: str | None = None, lat: float | None = None, long: float | None = None, db: Session = Depends(get_db)):
    logger.info(f"Hitted /getitemdb (sql): {f'id = {id}' if id  else f'lattitude = {lat}, longitude = {long}'}")
    if (not id) and (not lat) and (not long):
        logger.error("Any parameter not provided in /getitemdb (sql)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid criteria: Provide any one parameter to proceed")
    try:
        blog = db.query(Sales).filter(and_(Sales.id==id, and_(Sales.lat==lat, Sales.long==long))if id and (lat and long) else or_(Sales.id==id, and_(Sales.lat==lat, Sales.long==long))).all()

        logger.info(f"Successfully returned data containing {'id' if id else 'location'} in /getitemdb (sql)")
        return blog
    except Exception as e:
        logger.error(f"Error raised in /getitemdb: {str(e)} (sql)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/getitemistdb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def listitemdb(status: str | None = None, userid: str | None = None, db: Session = Depends(get_db)):
    logger.info(f"Hitted /getitemlistdb (sql): {f'status = {status}' if status else f'criteria = {userid}'}")
    if (not status) and (not userid):
        logger.error("Any parameter not provided in /getitemlistdb (sql)")
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Invalid Criteria: Provide any one parameter (status -- or -- userid) to proceed")
    try:
        
        blog = db.query(Sales).filter((and_(Sales.status==status, Sales.userId==userid))if status and userid else (or_(Sales.status==status, Sales.userId==userid))).all()
        
        logger.info(f"Successfully returned data of having {status} status and {userid} userId in /getitemlistdb (sql)")
        return blog
    except Exception as e:
        logger.error(f"Error raised in /getitemlistdb:\n {str(e)} (sql)")
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/get_items_in_radiusdb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def radiusdb(radius: float, latitude: float, longitude: float, db: Session = Depends(get_db)):
    logger.info(f"Hitted /get_items_in_radiusdb (sql): radius = {radius}, latitude = {latitude}, longitude = {longitude}")
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

            if distance<=radius:
                lst.append(user)

        logger.info(f"Successfully returned datapoints within radius of {radius}km from location [{latitude},{longitude}] in /get_item_in_radiusdb (sql)")
        return [user.__dict__ for user in lst]
    except Exception as e:
        logger.error(f"Error raised in /get_item_by_radiusdb: {str(e)} (sql)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/get_items_by_filterdb", tags=['SQL Db'], status_code=status.HTTP_202_ACCEPTED)
def multifilterdb(filterby: str, upper: int = None, lower: int = None, words: str | None = None, radius: float | None = None, latitude: float | None = None, longitude: float | None = None, db: Session = Depends(get_db)):

    if lower is None:
        lower = db.query(func.min(Sales.price)).scalar()

    if upper is None:
        upper = db.query(func.max(Sales.price)).scalar()

    if lower>upper:
        logger.error(f"Upper value {upper} less than lower value {lower} in /get_items_by_filterdb (sql)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid parameters: Upper value cannot be less than lower")
    
    if filterby not in ['price','desc','radius']:
        logger.error(f"Invalid filter value ({filterby}) provided in /get_items_by_filterdb (sql)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Parameter: Please provide valid filter")
    try:
        if filterby == 'price':
            logger.info(f"Hitted /get_items_by_filterdb (sql): filter = {filterby}, upper = {upper}, lower = {lower}")
            
            blog = db.query(Sales).filter(and_(Sales.price>=lower, Sales.price<=upper)).all()
            logger.info(f"Successfully returned data having prices from {lower} to {upper} in /get_items_by_filterdb (sql)")
            return blog
        elif filterby == 'desc':
            logger.info(f"Hitted /get_items_by_filterdb (sql): filter = {filterby}, words = {words}")
            blog = db.query(Sales).filter(Sales.description.like(f'%{words}%')).all()

            logger.info(f"Successfully returned data containing '{words}' in description from /get_items_by_filterdb (sql)")
            return blog
        elif filterby == 'radius':
            logger.info(f"Hitted /get_items_by_filterdb (sql): filter = {filterby}, radius = {upper}, lower = {lower}")
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

                if distance<=radius:
                    lst.append(user)
            logger.info(f"Successfully returned datapoints within radius of {radius}km from location [{latitude},{longitude}] in /get_items_by_filterdb (sql)")
            return [user.__dict__ for user in lst]
    
    except Exception as e:
        logger.error(f"Error raised in /get_items_by_filterdb: {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))