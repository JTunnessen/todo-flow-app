import logging
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Annotated, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

todos_db: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TodoFlow API starting up")
    yield
    logger.info("TodoFlow API shutting down")


app = FastAPI(title="TodoFlow API", version="1.0.0", lifespan=lifespan)


class TodoStatus:
    NEW = "New"
    IN_PROCESS = "In Process"
    DEFERRED = "Deferred"
    COMPLETE = "Complete"


VALID_STATUSES = [TodoStatus.NEW, TodoStatus.IN_PROCESS, TodoStatus.DEFERRED, TodoStatus.COMPLETE]


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    due_date: Optional[str] = Field(default=None)
    priority: int = Field(default=1, ge=1, le=10)
    status: str = Field(default=TodoStatus.NEW)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be in YYYY-MM-DD format")
        return v if v else None


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[str] = Field(default=None)
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    status: Optional[str] = Field(default=None)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be in YYYY-MM-DD format")
        return v if v else None


class TodoResponse(BaseModel):
    id: str
    title: str
    description: str
    due_date: Optional[str]
    priority: int
    status: str
    created_at: str
    updated_at: str
    is_overdue: bool


def compute_is_overdue(todo: dict) -> bool:
    if todo.get("due_date") and todo["status"] != TodoStatus.COMPLETE:
        try:
            due = datetime.strptime(todo["due_date"], "%Y-%m-%d").date()
            return due < date.today()
        except ValueError:
            return False
    return False


def todo_to_response(todo: dict) -> TodoResponse:
    return TodoResponse(
        id=todo["id"],
        title=todo["title"],
        description=todo["description"],
        due_date=todo.get("due_date"),
        priority=todo["priority"],
        status=todo["status"],
        created_at=todo["created_at"],
        updated_at=todo["updated_at"],
        is_overdue=compute_is_overdue(todo),
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "TodoFlow API"}


@app.get("/api/todos", response_model=List[TodoResponse])
def get_todos(
    status: Annotated[Optional[str], Query()] = None,
    priority: Annotated[Optional[int], Query(ge=1, le=10)] = None,
    sort_by: Annotated[Optional[str], Query()] = "created_at",
    sort_order: Annotated[Optional[str], Query()] = "desc",
):
    logger.info("GET /api/todos status=%s priority=%s sort_by=%s", status, priority, sort_by)
    items = list(todos_db.values())

    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status filter. Must be one of: {', '.join(VALID_STATUSES)}")
        items = [t for t in items if t["status"] == status]

    if priority is not None:
        items = [t for t in items if t["priority"] == priority]

    valid_sort_fields = {"created_at", "updated_at", "priority", "due_date", "title", "status"}
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"

    reverse = sort_order == "desc"

    def sort_key(t: dict):
        val = t.get(sort_by)
        if val is None:
            return "" if sort_by in {"due_date", "title", "status", "created_at", "updated_at"} else 0
        return val

    items.sort(key=sort_key, reverse=reverse)
    return [todo_to_response(t) for t in items]


@app.post("/api/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo_in: TodoCreate):
    logger.info("POST /api/todos title=%s", todo_in.title)
    now = datetime.utcnow().isoformat()
    todo_id = str(uuid.uuid4())
    todo = {
        "id": todo_id,
        "title": todo_in.title,
        "description": todo_in.description,
        "due_date": todo_in.due_date,
        "priority": todo_in.priority,
        "status": todo_in.status,
        "created_at": now,
        "updated_at": now,
    }
    todos_db[todo_id] = todo
    logger.info("Created todo id=%s", todo_id)
    return todo_to_response(todo)


@app.get("/api/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: str):
    logger.info("GET /api/todos/%s", todo_id)
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_to_response(todos_db[todo_id])


@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, todo_update: TodoUpdate):
    logger.info("PUT /api/todos/%s", todo_id)
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo = todos_db[todo_id]
    update_data = {k: v for k, v in todo_update.model_dump().items() if v is not None}
    if "due_date" in todo_update.model_dump() and todo_update.due_date is None:
        update_data["due_date"] = None
    todo.update(update_data)
    todo["updated_at"] = datetime.utcnow().isoformat()
    todos_db[todo_id] = todo
    logger.info("Updated todo id=%s", todo_id)
    return todo_to_response(todo)


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str):
    logger.info("DELETE /api/todos/%s", todo_id)
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos_db[todo_id]
    logger.info("Deleted todo id=%s", todo_id)
    return None


app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
