from fastapi import APIRouter, HTTPException, status
from src.log import logger
import json
import fastapi
import math

router = APIRouter(tags=["SQL Db"])

with open("data/sale.json") as f:
    data = json.load(f)

@router.get("/getsorteddata", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
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

@router.get("/getitem", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def singleitem(id: str | None = None, long: float | None = None, lat: float | None = None):
    logger.info(f"Hitted /getitem (json): {f'id = {id}' if id  else f'lattitude = {lat}, longitude = {long}'}")
    if (not id) and (not lat) and (not long):
        logger.error("Any parameter not provided in /getitem (josn)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid criteria: Provide any one parameter to proceed")
        
    try:
        logger.info(f"Successfully returned data containing {'id' if id else 'location'} in /getitem (json)")
        return [person for person in data if ((person['id']==id) and (person['loc']==[long,lat]) if id and (lat and long) else (person['id']==id) or (person['loc']==[long,lat]))]
    except Exception as e:
        logger.error(f"Error raised in /getitem:\n {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/getitemlist", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def listitem(status: str | None = None, userid: str | None = None):
    logger.info(f"Hitted /getitemlist (json): {f'status = {status}' if status else f'criteria = {userid}'}")
    if (not status) and (not userid):
        logger.error("Any parameter not provided in /getitemlist (json)")
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Invalid Criteria: Provide any one parameter (status -- or -- userid) to proceed")
    try:
        
        logger.info(f"Successfully returned data of having {status} status and {userid} userId in /getitemlist (josn)")
        return [person for person in data if ((person['status']==status) and (person['userId']==userid) if status and userid else (person['status']==status) or (person['iserId']==userid))]
    except Exception as e:
        logger.error(f"Error raised in /getitemlist: {str(e)} (json)")
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/get_items_in_radius", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
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

@router.get("/get_items_by_filter", tags=['Json'], status_code=status.HTTP_202_ACCEPTED)
def multifilter(filterby: str, upper: int | None = None, lower: int | None = None, words: str | None = None, radius: float | None = None, latitude: float | None = None, longitude: float | None = None):
    price = [person['price'] for person in data]
    if upper is None: upper = max(price)
    if lower is None: lower = min(price)

    if lower>upper:
        logger.error(f"Upper value {upper} less than lower value {lower} in /get_items_by_filter (json)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid parameters: Upper value cannot be less than lower")
    
    if filterby not in ['price','desc','radius']:
        logger.error(f"Invalid filter value ({filterby}) provided in /get_items_by_filter (json)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Parameter: Please provide valid filter")
    
    try:    
        if filterby == 'price':
            logger.info(f"Hitted /get_items_by_filter (json): filter = {filterby}, upper = {upper}, lower = {lower}")
            
            logger.info(f"Successfully returned data having prices from {lower} to {upper} in /get_items_by_filter (json)")
            return [person for person in data if ((person[filterby]>=lower) and (person[filterby]<=upper))]
        
        elif filterby == 'desc':
            logger.info(f"Hitted /get_items_by_filter (json): filter = {filterby}, words = {words}")
            for person in data:
                if person['description'] != None:
                    if words in person['description']:
                        logger.info(f"Successfully returned data containing '{words}' in description from /get_items_by_filter (json)")
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
                
                if distance<=radius:
                    lst.append(person)

            logger.info(f"Successfully returned datapoints within radius of {radius}km from location [{latitude},{longitude}] in /get_items_by_filter (json)")
            return lst
            
    except Exception as e:
        logger.error(f"Error raised in /get_items_by_filter: {str(e)} (json)")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
