from pydantic import BaseModel


class Question(BaseModel):
    question: str


class TTSRequest(BaseModel):
    text: str