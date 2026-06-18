from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gtts import gTTS
import io
from config import THRESHOLD_SIMILARITY
from app.llm import answer, local_llm
from app.retriever import retrieve, build_context

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


class Question(BaseModel):
    question: str

# static files (optional)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/chat")
def chat(q: Question):
    res = retrieve(q.question)
    chunks = res['chunks']

    if not chunks or chunks[0]["similarity"] < THRESHOLD_SIMILARITY:
        return {
            "answer": "Nội dung câu hỏi hiện chưa đủ cơ sở pháp lý để đối chiếu với các quy định hiện hành. Vui lòng liên hệ chuyên gia để được tư vấn cụ thể hơn.",
            "citations": []
        }

    context_text = build_context(res['chunks'], res['facts'])
    answer_text = answer(q.question, context_text)

    citations = [{
        "chunk_id": chunks[0]["chunk_id"],
        "content": chunks[0]["content"]
    }]

    return {
        "answer": answer_text,
        "citations": citations
    }

@app.post("/tts")
async def tts(data: dict):
    text = data["text"]
    tts = gTTS(text, lang="vi")

    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="audio/mpeg")
