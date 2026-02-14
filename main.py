from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()

# in-memory JSON storage (not persistent)
todos = []
next_id = 1


class TodoIn(BaseModel):
    text: str


@app.get("/todos")
async def get_todos():
    return todos


@app.post("/todos")
async def add_todo(todo: TodoIn):
    global next_id
    item = {"id": next_id, "text": todo.text, "done": False}
    todos.append(item)
    next_id += 1
    return item


@app.put("/todos/{todo_id}")
async def mark_done(todo_id: int):
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = True
            return t
    raise HTTPException(status_code=404, detail="Not found")


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            return todos.pop(i)
    raise HTTPException(status_code=404, detail="Not found")