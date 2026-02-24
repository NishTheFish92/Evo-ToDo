from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from Routers.auth_app import get_current_user
from fastapi import Depends
from bson import ObjectId
import datetime

router = APIRouter()

# in-memory JSON storage (not persistent)
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["todo"]
tasks = db["tasks"]

@router.get("/todos")
async def get_todos(current_user : str = Depends(get_current_user)):
    usertasks = await tasks.find({"user_id": current_user["_id"]}).to_list(length=None)
    return usertasks
    



@router.post("/todos")
async def add_todo(todo: str,current_user : str = Depends(get_current_user)):
    try:
        await tasks.insert_one({
            "user_id" : current_user["_id"],
            "title" : todo,
            "completed" : False,
            "created_at" : datetime.utcnow()
        })

    except:
        raise HTTPException(status_code=500, detail="Database insert failed")



@router.put("/todos/{todo_id}")
async def mark_done(todo_id: str, current_user : str = Depends(get_current_user)):
    result = await tasks.update_one(
        {
            "_id" : ObjectId(todo_id),
            "user_id" : current_user["_id"]
        },
        {"$bit" : {"completed" : {"xor" : 1}}}
        )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str, current_user : str = Depends(get_current_user)):
    result = await tasks.delete_one(
        {
            "_id" : ObjectId(todo_id),
            "user_id" : current_user["_id"]
        }
        )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")