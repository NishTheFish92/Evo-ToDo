# Evo-ToDo

Evo-ToDo is a simple FastAPI-based backend for a todo application with authentication support.

## Features
- User authentication
- Todo management (CRUD operations)
- Modular router structure

## Project Structure
```
main.py            # FastAPI app entry point
Routers/
  auth_app.py      # Authentication routes
  todo.py          # Todo routes
pyproject.toml     # Project configuration
README.md          # Project documentation
```

## Setup
1. Initialize the project and environment using uv:
   ```bash
   uv init
   uv venv
   uv sync
   ```

## Running the Server
Start the FastAPI server with:
```bash
uvicorn main:app --reload
```

## API Endpoints
### Authentication Endpoints

- **POST /auth/register**: Register a new user with username and password.
- **POST /auth/login**: Authenticate user and return access token.

### Todo Endpoints

- **GET /todos**: Get all todos for the authenticated user.
- **POST /todos/new**: Add a new todo for the authenticated user.
- **PATCH /todos/{todo_id}**: Toggle completion status of a todo by its ID.
- **DELETE /todos/delete/{todo_id}**: Delete a todo by its ID for the authenticated user.


