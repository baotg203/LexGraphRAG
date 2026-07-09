from pydantic import BaseModel
from typing import Optional


class Question(BaseModel):
    question: str
    session_id: Optional[str] = None


class TTSRequest(BaseModel):
    text: str