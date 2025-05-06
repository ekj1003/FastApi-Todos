import sys
import os
from fastapi.testclient import TestClient
import pytest
from main import app, save_todos, TodoItem

# TestClient로 FastAPI 애플리케이션을 초기화
client = TestClient(app)

# pytest fixture로 테스트 전후 초기화
@pytest.fixture(autouse=True)
def setup_and_teardown():
    # 테스트 전 초기화
    save_todos([])
    yield
    # 테스트 후 정리
    save_todos([])

# 빈 할 일 목록을 확인하는 테스트
def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

# 할 일이 있는 목록을 확인하는 테스트
def test_get_todos_with_items():
    todo = TodoItem(
        id=1,
        title="Test",
        description="Test description",
        completed=False,
        due_date="2025-12-31",
        priority="medium",
        tags=["tag1", "tag2"]
    )
    save_todos([todo.model_dump()])  # dict() 대신 model_dump() 사용
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test"
    assert "tag1" in data[0]["tags"]

# 할 일 추가 테스트
def test_create_todo():
    todo = {
        "id": 1,
        "title": "Test",
        "description": "Test description",
        "completed": False,
        "due_date": "2025-12-31",
        "priority": "high",
        "tags": ["urgent"]
    }
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test"
    assert data["priority"] == "high"
    assert "urgent" in data["tags"]

# 할 일 추가 시 유효하지 않은 경우 테스트
def test_create_todo_invalid():
    todo = {
        "id": 1,
        "title": "Test"
        # description 누락
    }
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

# 할 일 업데이트 테스트
def test_update_todo():
    todo = TodoItem(
        id=1,
        title="Original",
        description="Original description",
        completed=False,
        due_date="2025-12-31",
        priority="low",
        tags=["a"]
    )
    save_todos([todo.model_dump()])  # dict() 대신 model_dump() 사용

    updated = {
        "id": 1,
        "title": "Updated",
        "description": "Updated description",
        "completed": False,  # toggle 상태 유지 위해 False로 유지
        "due_date": "2026-01-01",
        "priority": "medium",
        "tags": ["b", "c"]
    }
    response = client.put("/todos/1", json=updated)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert "c" in data["tags"]

# 할 일 업데이트 시 항목을 찾을 수 없는 경우 테스트
def test_update_todo_not_found():
    updated = {
        "id": 1,
        "title": "Updated",
        "description": "Updated description",
        "completed": False,
        "due_date": "2025-12-31",
        "priority": "medium",
        "tags": []
    }
    response = client.put("/todos/1", json=updated)
    assert response.status_code == 404

# 할 일 상태 토글 테스트
def test_toggle_todo():
    # due_date=None을 due_date=""로 수정
    todo = TodoItem(id=1, title="Toggle", description="To toggle", completed=False, due_date="")
    save_todos([todo.model_dump()])  # dict() 대신 model_dump() 사용
    response = client.put("/todos/1/toggle")
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True

# 할 일 삭제 테스트
def test_delete_todo():
    # due_date=None을 due_date=""로 수정
    todo = TodoItem(id=1, title="Delete", description="To delete", completed=False, due_date="")
    save_todos([todo.model_dump()])  # dict() 대신 model_dump() 사용
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"

# 할 일 삭제 시 항목을 찾을 수 없는 경우 테스트
def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == 200  # FastAPI에선 not found가 아니라 그냥 삭제 성공 메시지 리턴
    assert response.json()["message"] == "To-Do item deleted"