from fastapi import FastAPI,Request
import googlemaps.client
from pydantic import BaseModel
from pandas import read_csv
import math
from dotenv import load_dotenv
import os 
import googlemaps

#load_dotenv()

url = os.getenv("url")
mapsAPI = os.getenv("googleMapsAPI")

#url = os.environ("url")
#mapsAPI = os.environ("googleMapsAPI")

gmaps = googlemaps.Client(key = mapsAPI)

def haversine_distance(lat1, long1, lat2, long2):
    # Convert coordinates from degrees to radians
    lat1_rad, long1_rad = math.radians(lat1), math.radians(long1)
    lat2_rad, long2_rad = math.radians(lat2), math.radians(long2)

    # Calculate differences
    delta_lat = lat2_rad - lat1_rad
    delta_long = long2_rad - long1_rad

    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_long / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of the Earth in kilometers
    R = 6371.0

    # Calculate the distance
    distance_km = R * c

    return distance_km


def calculateDist(userLat,userLon,userSpecifiedDistance) -> dict:
    stops={}
    data = read_csv(url)
    i=0
    for index,row in data.iterrows():
        lat1 = row["LATITUDE"]
        lon1 = row["LONGITUDE"]
        #print(lat1,lon1)
        distance = haversine_distance(userLat,userLon,lat1,lon1)

        if (distance<=userSpecifiedDistance):
            #print(row["ROUTE_NO"],row["STOP_NAME"])
            stops[i]={"Route_no":row["ROUTE_NO"],"Stop_name":row["STOP_NAME"],"Latitude":row["LATITUDE"],"Longitude":row["LONGITUDE"],"Timing":row["TIMING"],"Distance":distance}
            i+=1 
        
    if i==0:
        stops["status"] = "No Stops Found"
    else:
        stops["status"] = "Stops Found"

    return stops

def routeData(routes):
    #print(routes)
    
    stops={}
    data = read_csv(url)
    i=0
    for index,row in data.iterrows():
        #print(row['ROUTE_NO'])
        if  ("All Routes" in routes) or (row['ROUTE_NO'] in routes):
            stops[i]={"Route_no":row["ROUTE_NO"],"Stop_name":row["STOP_NAME"],"Latitude":row["LATITUDE"],"Longitude":row["LONGITUDE"],"Timing":row["TIMING"]}
            i+=1 
        
    if i==0:
        stops["status"] = "No Stops Found"
    else:
        stops["status"] = "Stops Found"

    return stops



app = FastAPI()

class userLocation(BaseModel):
    latitude:float
    longitude:float 
    distance:float

class address(BaseModel):
    address:str


class routes(BaseModel):
    routes:list

@app.get("/calculateDistance")
async def haversine(calcualteDistance:userLocation,request:Request):
    data=dict(calcualteDistance)
    userLat = data["latitude"]
    userLon = data["longitude"]
    userPreferedDistance = data["distance"]
    print(userLat,userLon)
    result = calculateDist(userLat,userLon,userPreferedDistance)
    return result

@app.get("/findGeoCoordinates")
async def findCoorinates(findGeoCoordinates:address,request:Request):
    data = dict(findGeoCoordinates)
    address = data["address"]

    try:
        geocode = gmaps.geocode(address)
    except :
        pass 
    
    geocode = geocode[0]["geometry"]

    lat = geocode["location"]["lat"]
    lon = geocode["location"]["lng"]

    if (lon > 78 and lon < 81) and (lat >11 and lat <14):
        return {"status":"In Scope","latitude":lat,"longitude":lon}
    
    else:
        return {"status":"Not in scope"}

@app.get("/routes")
async def returnRoutes(routes:routes):
    """
    Used to get all the data
    usecase: To retrieve the routeno,stopname,lat,lon,time
    """
    data = dict(routes)
    return routeData(data["routes"])

@app.get("/routeNames")
async def returnUniqueRouteNames():
    """
    Used to get all the unique route names
    usecase: To display route names in the checkbox
    """
    data = read_csv(url)
    return {"routeNames":data["ROUTE_NO"].unique().tolist()}
