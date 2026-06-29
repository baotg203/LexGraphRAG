from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import (
    HTMLResponse,
    StreamingResponse
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.src.models.chat import (
    Question,
    TTSRequest
)
from app.src.container import QAContainer
from app.core.db import get_connection
from app.core.graph import neo4j_driver

conn = get_connection()

container = QAContainer(db=conn, neo4j_driver=neo4j_driver)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    container.close()


app = FastAPI(
    title="Legal Chatbot",
    lifespan=lifespan
)

templates = Jinja2Templates(
    directory="app/templates"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# ==========================
# Home
# ==========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


# ==========================
# Chat
# ==========================

@app.post("/chat")
async def chat(q: Question):
    return container.chat_service.ask(
        q.question
    )


# ==========================
# Text To Speech
# ==========================

@app.post("/tts")
async def tts(data: TTSRequest):
    audio = container.tts_service.generate(
        data.text
    )

    return StreamingResponse(
        audio,
        media_type="audio/mpeg"
    )