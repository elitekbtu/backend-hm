from fastapi import FastAPI
from .tasks import my_task
from .database import engine
from . import models
from pydantic import BaseModel
from fastapi import HTTPException
from .assistant import get_provider, AIProvider
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend (e.g. http://localhost:5173). In production, restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Эндпоинт для проверки состояния сервиса Docker'ом."""
    return {"status": "ok"}

@app.get("/")
def read_root():
    """Корневой эндпоинт."""
    return {"Hello": "World"}

@app.post("/start-task")
async def start_task():
    """Запускает фоновую задачу Celery."""
    task = my_task.delay(5)
    return {"task_id": task.id}

@app.on_event("startup")
def on_startup():
    """Create database tables if they do not exist."""
    models.Base.metadata.create_all(bind=engine)

class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat/{provider}", response_model=ChatResponse)
async def chat_with_provider(provider: str, request: ChatRequest):
    """Общение с выбранным AI провайдером.
    Передайте текст запроса и получите ответ от модели.
    """
    try:
        ai: AIProvider = get_provider(provider)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        reply = await ai.chat(request.prompt)
    except Exception as exc:  # pragma: no cover
        # Surface the provider error message to the client for easier debugging
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(response=reply)