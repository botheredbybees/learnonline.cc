from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.quiz import QuizQuestion, QuizAnswer, UserQuizAttempt
from ..models.quiz import UserTextResponse, UserDragDropResponse, QuestionFeedback
from ..models.quiz import QuizQuestionElement, QuizQuestionCriticalAspect
from ..models.tables import UnitElement, UnitCriticalAspect

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class QuizQuestionCreate(BaseModel):
    question_text: str
    question_type: str
    difficulty_level: int
    experience_points: int
    unit_id: int

class QuizAnswerCreate(BaseModel):
    answer_text: str
    is_correct: bool
    question_id: int

class UserQuizAttemptCreate(BaseModel):
    user_id: int
    unit_id: int

class UserTextResponseCreate(BaseModel):
    attempt_id: int
    question_id: int
    response_text: str
    is_correct: bool

class UserDragDropResponseCreate(BaseModel):
    attempt_id: int
    question_id: int
    answer_order: List[int]
    is_correct: bool

class QuestionFeedbackCreate(BaseModel):
    user_id: int
    question_id: int
    is_upvote: bool
    feedback_text: Optional[str] = None
    suggested_improvement: Optional[str] = None
@router.post("/question/{question_id}/link-element/{element_id}")
def link_question_to_element(
    question_id: int, 
    element_id: int, 
    db: Session = Depends(get_db)
):
    # Verify question exists
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Verify element exists
    element = db.query(UnitElement).filter(UnitElement.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Create the relationship
    relationship = QuizQuestionElement(
        question_id=question_id,
        element_id=element_id
    )
    db.add(relationship)
    db.commit()
    return {"message": "Question successfully linked to element"}

@router.post("/question/{question_id}/link-critical-aspect/{aspect_id}")
def link_question_to_critical_aspect(
    question_id: int, 
    aspect_id: int, 
    db: Session = Depends(get_db)
):
    # Verify question exists
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Verify critical aspect exists
    aspect = db.query(UnitCriticalAspect).filter(UnitCriticalAspect.id == aspect_id).first()
    if not aspect:
        raise HTTPException(status_code=404, detail="Critical aspect not found")
    
    # Create the relationship
    relationship = QuizQuestionCriticalAspect(
        question_id=question_id,
        critical_aspect_id=aspect_id
    )
    db.add(relationship)
    db.commit()
    return {"message": "Question successfully linked to critical aspect"}

@router.get("/unit/{unit_id}/questions", response_model=List[QuizQuestion])
def get_questions_by_unit(unit_id: int, db: Session = Depends(get_db)):
    return db.query(QuizQuestion).filter(QuizQuestion.unit_id == unit_id).all()

@router.get("/element/{element_id}/questions", response_model=List[QuizQuestion])
def get_questions_by_element(element_id: int, db: Session = Depends(get_db)):
    return (
        db.query(QuizQuestion)
        .join(QuizQuestionElement)
        .filter(QuizQuestionElement.element_id == element_id)
        .all()
    )

@router.get("/critical-aspect/{aspect_id}/questions", response_model=List[QuizQuestion])
def get_questions_by_critical_aspect(aspect_id: int, db: Session = Depends(get_db)):
    return (
        db.query(QuizQuestion)
        .join(QuizQuestionCriticalAspect)
        .filter(QuizQuestionCriticalAspect.critical_aspect_id == aspect_id)
        .all()
    )