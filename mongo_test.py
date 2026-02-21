from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

client = AsyncIOMotorClient("mongodb://localhost:27017")
app = FastAPI()
db = client["mydatabase"]
collection = db["users"]
@app.get("/test")
async def test():
    await collection.insert_one({"name":"test"})
    return {"done" : True}