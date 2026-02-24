from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

# in-memory JSON storage (not persistent)
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["todo"]
tasks = db["tasks"]



class TodoIn(BaseModel):
    text: str


@router.get("/todos")
async def get_todos():
    


@router.post("/todos")
async def add_todo(todo: TodoIn):
    global next_id
    item = {"id": next_id, "text": todo.text, "done": False}
    todos.append(item)
    next_id += 1
    return item


@router.put("/todos/{todo_id}")
async def mark_done(todo_id: int):
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = True
            return t
    raise HTTPException(status_code=404, detail="Not found")


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            return todos.pop(i)
    raise HTTPException(status_code=404, detail="Not found")