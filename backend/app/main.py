from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import random
from datetime import datetime

from .database import Base, engine, get_db
from . import models, schemas, auth

app = FastAPI(title="LeadMasters Exam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

@app.post("/auth/register", response_model=schemas.Token)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=data.email, password_hash=auth.hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    access = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": access}

@app.post("/auth/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not auth.verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": access}

@app.get("/exam/start", response_model=schemas.StartExamResponse)
def start_exam(limit: int = 10, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    all_qs = db.query(models.Question).all()
    if not all_qs:
        raise HTTPException(status_code=400, detail="No questions in database. Run seed endpoint.")
    pick = random.sample(all_qs, k=min(limit, len(all_qs)))
    session = models.ExamSession(user_id=user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    # Return questions without 'correct'
    out = [schemas.QuestionOut.model_validate(q) for q in pick]
    return {"session_id": session.id, "questions": out}

@app.post("/exam/submit", response_model=schemas.ResultOut)
def submit(payload: schemas.SubmitPayload, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    session = db.query(models.ExamSession).filter(models.ExamSession.id == payload.session_id, models.ExamSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.submitted:
        # idempotent response
        total = db.query(models.Question).count()
        return {"session_id": session.id, "score": session.score, "total": total}
    # time check
    now = datetime.utcnow()
    elapsed = (now - session.started_at).total_seconds()
    if elapsed > session.duration_seconds:
        # Auto-submit behavior: proceed, but no new answers allowed (we still grade current payload)
        pass
    # grade
    score = 0
    for qid, choice in payload.answers.items():
        q = db.query(models.Question).filter(models.Question.id == int(qid)).first()
        if not q:
            continue
        if choice.lower() == q.correct.lower():
            score += 1
        # store answer
        ans = models.Answer(session_id=session.id, question_id=q.id, choice=choice.lower())
        db.add(ans)
    session.score = score
    session.submitted = True
    db.commit()
    total = db.query(models.Question).count()
    return {"session_id": session.id, "score": score, "total": total}

@app.get("/exam/result/{session_id}", response_model=schemas.ResultOut)
def result(session_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    session = db.query(models.ExamSession).filter(models.ExamSession.id == session_id, models.ExamSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    total = db.query(models.Question).count()
    return {"session_id": session.id, "score": session.score, "total": total}

# Simple seeding endpoint for demo (not for production)
@app.post("/dev/seed")
def seed(db: Session = Depends(get_db)):
    if db.query(models.Question).count() > 0:
        return {"ok": True, "message": "Already seeded"}
    sample = [
        {"text": "What is the capital of France?", "option_a": "Berlin", "option_b": "Paris", "option_c": "Madrid", "option_d": "Rome", "correct": "b"},
        {"text": "2 + 2 = ?", "option_a": "3", "option_b": "5", "option_c": "4", "option_d": "22", "correct": "c"},
        {"text": "React is a ____ library.", "option_a": "UI", "option_b": "Database", "option_c": "OS", "option_d": "Compiler", "correct": "a"},
        {"text": "HTTP status 200 means?", "option_a": "OK", "option_b": "Created", "option_c": "Not Found", "option_d": "Forbidden", "correct": "a"},
        {"text": "JWT stands for?", "option_a": "Java Web Tool", "option_b": "JSON Web Token", "option_c": "JavaScript Web Type", "option_d": "None", "correct": "b"},
        {"text": "SQL command to fetch rows?", "option_a": "SELECT", "option_b": "INSERT", "option_c": "UPDATE", "option_d": "DELETE", "correct": "a"},
        {"text": "Which is a NoSQL DB?", "option_a": "MongoDB", "option_b": "PostgreSQL", "option_c": "MySQL", "option_d": "SQLite", "correct": "a"},
        {"text": "CSS property for text color?", "option_a": "background", "option_b": "color", "option_c": "font-weight", "option_d": "border", "correct": "b"},
        {"text": "In React, useState returns?", "option_a": "value and setter", "option_b": "class", "option_c": "DOM", "option_d": "route", "correct": "a"},
        {"text": "Primary key property?", "option_a": "Duplicates ok", "option_b": "Must be unique", "option_c": "Nullable", "option_d": "Text only", "correct": "b"}
    ]
    for q in sample:
        db.add(models.Question(**q))
    db.commit()
    return {"ok": True, "inserted": len(sample)}
