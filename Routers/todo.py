from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from Routers.auth_app import get_current_user
from fastapi import Depends
from bson import ObjectId,errors
from datetime import datetime,timezone

router = APIRouter()

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["todo"]
tasks = db["tasks"]

class task_create(BaseModel):
    title: str

@router.get("/todos")
async def get_todos(current_user : dict = Depends(get_current_user)):
    usertasks = await tasks.find({"user_id": current_user["_id"]}).to_list(length=None)
    for i in usertasks:
        i["_id"] = str(i["_id"])
        i["user_id"] = str(i["user_id"])
    return usertasks
    



@router.post("/todos/new")
async def add_todo(todo: task_create,current_user : dict = Depends(get_current_user)):
    new_task = {
        "user_id" : current_user["_id"],
        "title" : todo.title,
        "completed" : False,
        "created_at" : datetime.now(timezone.utc)
    }
    await tasks.insert_one(new_task)
    new_task["_id"] = str(new_task["_id"])
    new_task["user_id"] = str(new_task["user_id"])
    return new_task




@router.patch("/todos/{todo_id}")
async def mark_done(todo_id: str, current_user : dict = Depends(get_current_user)):
    try:
        result = await tasks.update_one(
            {
                "_id" : ObjectId(todo_id),
                "user_id" : current_user["_id"]
            },
            [{"$set": {"completed": {"$not": "$completed"}}}]
            )
    except errors.InvalidId:
        raise HTTPException(status_code=400,detail = "Invalid object ID")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Task updated successfully"}



@router.delete("/todos/delete/{todo_id}")
async def delete_todo(todo_id: str, current_user : dict = Depends(get_current_user)):
    try:
        result = await tasks.delete_one(
            {
                "_id" : ObjectId(todo_id),
                "user_id" : current_user["_id"]
            }
            )
    except errors.InvalidId:
        raise HTTPException(status_code=400,detail = "Invalid object ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message" : "Task deleted successfully"}