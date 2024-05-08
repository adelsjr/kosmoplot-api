from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson.objectid import ObjectId

app = FastAPI()

# Database: MongoDB connection URL
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["kosmoplotdb"]
collection = database["stars"]

# Model: Star
class Star(BaseModel):
    name: str 
    constellation: str 
    right_ascension: str 
    declination: str
    apparent_magnitude: float
    absolute_magnitude: float
    distance_light_year: int
    spectral_class: str = None


# Routes
@app.post("/stars/", response_model=Star)
async def create_star(star: Star):
    result = await collection.insert_one(star.model_dump())
    print("result %s" % repr(result))
    new_star = await collection.find_one({"_id": result.inserted_id})
    return new_star

@app.get("/stars/", response_model=list[Star])
async def retrieve_items(
    name: list[str] = Query([], title="Star names to retrieve. Accepts a list."),
    constellation: list[str] = Query([], title="Stars from a given constellation to retrieve. Accepts a list.")
):
    result = []
    query = {}
    if name:
        query = {"name" : {"$in" : name}}
    if constellation:
        query = {"constellation" : {"$in" : constellation}}

    async for star in collection.find(query):
        result.append(star)
    return result

@app.get("/stars/{id}", response_model=Star)
async def read_item(id: str):
    star = await collection.find_one({"_id": ObjectId(id)})
    if star:
        return star
    raise HTTPException(status_code=404, detail="Star not found")

@app.delete("/stars/{id}", response_model=Star)
async def delete_item(id: str):
    deleted_item = await collection.find_one_and_delete({"_id": ObjectId(id)})
    if deleted_item:
        return deleted_item
    raise HTTPException(status_code=404, detail="Item not found")
