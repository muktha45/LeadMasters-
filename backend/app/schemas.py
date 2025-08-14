from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class QuestionOut(BaseModel):
    id: int
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True

class StartExamResponse(BaseModel):
    session_id: int
    questions: List[QuestionOut]

class SubmitPayload(BaseModel):
    session_id: int
    answers: Dict[int, str]  # question_id -> 'a'/'b'/'c'/'d'

class ResultOut(BaseModel):
    session_id: int
    score: int
    total: int
