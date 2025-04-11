from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os

app = FastAPI()

class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    due_date: str = None
    priority: str = "low"
    tags: list[str] = []  # ✅ 태그 필드 추가

TODO_FILE = "todo.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as file:
            return json.load(file)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file, indent=4)

@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for index, todo in enumerate(todos):
        if todo["id"] == todo_id:
            updated_data = updated_todo.dict()
            updated_data["completed"] = todo["completed"]  # 완료 상태 유지
            todos[index] = updated_data
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.put("/todos/{todo_id}/toggle", response_model=TodoItem)
def toggle_todo(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            save_todos(todos)
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return {"message": "To-Do item deleted"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)
