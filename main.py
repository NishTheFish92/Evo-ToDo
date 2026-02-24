from fastapi import FastAPI
from Routers.auth_app import router as auth_router
from Routers.todo import router as todo_router
app = FastAPI()

app.include_router(auth_router)
app.include_router(todo_router)

