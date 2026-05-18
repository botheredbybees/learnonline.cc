"""M2 Quiz Router — student-facing quiz endpoints."""

import random
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.auth_bearer import JWTBearer
from auth.auth_handler import decode_jwt, get_user_with_role
from database import get_db
import models.tables as models
from models.schemas import (
    AnswerResponse,
    AnswerSubmission,
    ElementProgressResponse,
    ElementStatusSchema,
    QuestionResponse,
    UnitProgressResponse,
    UnitQuizStateResponse,
)

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

_ANSWER_KEYS = {"correct", "correct_order", "keywords", "model_answer"}


def _strip_answer_keys(options: dict) -> dict:
    return {k: v for k, v in options.items() if k not in _ANSWER_KEYS}


# ── auth helper ──────────────────────────────────────────────────────────────


def _get_current_user(
    token: str = Depends(JWTBearer()), db: Session = Depends(get_db)
) -> models.User:
    """Decode the Bearer token supplied by JWTBearer and return the User ORM object."""
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = get_user_with_role(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    return user


# ── graders ──────────────────────────────────────────────────────────────────


def _grade_mcq(options: dict, answer: dict) -> tuple[bool, str]:
    correct = options.get("correct")
    selected = answer.get("selected")
    explanation = options.get("explanation", "")
    return selected == correct, explanation


def _grade_short_answer(options: dict, answer: dict) -> tuple[bool, str]:
    keywords = [k.lower() for k in options.get("keywords", [])]
    response = answer.get("text", "").lower()
    matched = any(kw in response for kw in keywords)
    return matched, options.get("model_answer", "")


def _grade_ordering(options: dict, answer: dict) -> tuple[bool, str]:
    correct_order = options.get("correct_order", [])
    submitted = answer.get("order", [])
    is_correct = submitted == correct_order
    items = options.get("items", [])
    explanation = "Correct order: " + ", ".join(
        str(items[i]) for i in correct_order if i < len(items)
    )
    return is_correct, explanation


_GRADERS = {
    "mcq": _grade_mcq,
    "short_answer": _grade_short_answer,
    "ordering": _grade_ordering,
}

# ── db helpers ────────────────────────────────────────────────────────────────


def _session_correct_count(
    db: Session, user_id: int, assessment_id: int, session_id: str
) -> int:
    return (
        db.query(func.count(models.UserAnswer.question_id.distinct()))
        .filter(
            models.UserAnswer.user_id == user_id,
            models.UserAnswer.session_id == session_id,
            models.UserAnswer.is_correct == True,
        )
        .join(models.AssessmentQuestion)
        .filter(models.AssessmentQuestion.assessment_id == assessment_id)
        .scalar()
    )


def _total_active_questions(db: Session, assessment_id: int) -> int:
    return (
        db.query(models.AssessmentQuestion)
        .filter_by(
            assessment_id=assessment_id, is_active=True, review_status="approved"
        )
        .count()
    )


def _award_xp(db: Session, user_id: int, points: int) -> None:
    """Increment UserProfile.experience_points directly (profile must already exist)."""
    profile = db.query(models.UserProfile).filter_by(user_id=user_id).first()
    if profile is None:
        profile = models.UserProfile(user_id=user_id, experience_points=0, level=1)
        db.add(profile)
        db.flush()
    profile.experience_points = (profile.experience_points or 0) + points


# ── endpoints ─────────────────────────────────────────────────────────────────


@router.get("/units/{unit_id}/quiz-state")
def get_quiz_state(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_get_current_user),
) -> UnitQuizStateResponse:
    unit = db.query(models.Unit).filter_by(id=unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    elements = (
        db.query(models.UnitElement)
        .filter_by(unit_id=unit_id)
        .order_by(models.UnitElement.element_num)
        .all()
    )
    element_statuses: List[ElementStatusSchema] = []
    for el in elements:
        prog = (
            db.query(models.UserElementProgress)
            .filter_by(user_id=current_user.id, element_id=el.id)
            .first()
        )
        element_statuses.append(
            ElementStatusSchema(
                element_id=el.id,
                element_num=el.element_num,
                element_text=el.element_text,
                status=prog.status if prog else "not_started",
                attempts=prog.attempts if prog else 0,
                xp_awarded=prog.xp_awarded if prog else None,
            )
        )

    return UnitQuizStateResponse(
        unit_id=unit.id,
        unit_code=unit.code,
        unit_title=unit.title,
        plain_english_description=unit.plain_english_description,
        elements=element_statuses,
    )


@router.get("/elements/{element_id}/questions")
def get_element_questions(
    element_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_get_current_user),
) -> List[QuestionResponse]:
    assessment = db.query(models.Assessment).filter_by(element_id=element_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="No quiz for this element")

    questions = (
        db.query(models.AssessmentQuestion)
        .filter_by(
            assessment_id=assessment.id, is_active=True, review_status="approved"
        )
        .all()
    )
    random.shuffle(questions)
    return [
        QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=_strip_answer_keys(q.options or {}),
            pc_id=q.pc_id,
        )
        for q in questions
    ]


@router.post("/answer")
def submit_answer(
    payload: AnswerSubmission,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_get_current_user),
) -> AnswerResponse:
    question = (
        db.query(models.AssessmentQuestion).filter_by(id=payload.question_id).first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    grader = _GRADERS.get(question.question_type)
    if not grader:
        raise HTTPException(
            status_code=400, detail=f"Unknown question type: {question.question_type}"
        )

    is_correct, explanation = grader(question.options or {}, payload.answer)

    db.add(
        models.UserAnswer(
            user_id=current_user.id,
            question_id=payload.question_id,
            session_id=payload.session_id,
            answer=payload.answer,
            is_correct=is_correct,
        )
    )
    db.flush()

    assessment = (
        db.query(models.Assessment).filter_by(element_id=payload.element_id).first()
    )
    if assessment and question.assessment_id != assessment.id:
        raise HTTPException(
            status_code=400, detail="Question does not belong to this element"
        )
    xp_per_element = assessment.experience_points if assessment else 50

    element_passed = False
    xp_awarded: Optional[int] = None
    unit_completed = False
    badge_awarded: Optional[str] = None

    if assessment:
        total_q = _total_active_questions(db, assessment.id)
        session_correct = _session_correct_count(
            db, current_user.id, assessment.id, payload.session_id
        )

        if total_q > 0 and session_correct >= total_q:
            prog = (
                db.query(models.UserElementProgress)
                .filter_by(user_id=current_user.id, element_id=payload.element_id)
                .first()
            )

            if prog is None or prog.status != "passed":
                element = (
                    db.query(models.UnitElement)
                    .filter_by(id=payload.element_id)
                    .first()
                )
                if element is None:
                    raise HTTPException(status_code=404, detail="Element not found")
                if prog is None:
                    prog = models.UserElementProgress(
                        user_id=current_user.id,
                        element_id=payload.element_id,
                        unit_id=element.unit_id,
                    )
                    db.add(prog)
                    db.flush()
                prog.status = "passed"
                prog.xp_awarded = xp_per_element
                prog.attempts = (prog.attempts or 0) + 1
                prog.passed_at = datetime.now(timezone.utc)
                db.flush()

                _award_xp(db, current_user.id, xp_per_element)
                element_passed = True
                xp_awarded = xp_per_element

                # Check whether all elements in the unit are now passed
                all_elements = (
                    db.query(models.UnitElement)
                    .filter_by(unit_id=element.unit_id)
                    .all()
                )
                passed_count = (
                    db.query(models.UserElementProgress)
                    .filter(
                        models.UserElementProgress.user_id == current_user.id,
                        models.UserElementProgress.element_id.in_(
                            [e.id for e in all_elements]
                        ),
                        models.UserElementProgress.status == "passed",
                    )
                    .count()
                )

                if passed_count == len(all_elements):
                    unit_completed = True
                    unit = db.query(models.Unit).filter_by(id=element.unit_id).first()
                    badge = db.query(models.Badge).filter_by(code=unit.code).first()
                    if badge is None:
                        badge = (
                            db.query(models.Badge)
                            .filter_by(title="Unit Complete")
                            .first()
                        )
                    if badge:
                        already = (
                            db.query(models.UserBadge)
                            .filter_by(user_id=current_user.id, badge_id=badge.id)
                            .first()
                        )
                        if not already:
                            db.add(
                                models.UserBadge(
                                    user_id=current_user.id, badge_id=badge.id
                                )
                            )
                        badge_awarded = badge.title

    db.commit()

    return AnswerResponse(
        is_correct=is_correct,
        explanation=explanation or None,
        element_passed=element_passed,
        xp_awarded=xp_awarded,
        unit_completed=unit_completed,
        badge_awarded=badge_awarded,
    )


@router.get("/units/{unit_id}/progress")
def get_unit_progress(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_get_current_user),
) -> UnitProgressResponse:
    elements = (
        db.query(models.UnitElement)
        .filter_by(unit_id=unit_id)
        .order_by(models.UnitElement.element_num)
        .all()
    )
    result: List[ElementProgressResponse] = []
    for el in elements:
        prog = (
            db.query(models.UserElementProgress)
            .filter_by(user_id=current_user.id, element_id=el.id)
            .first()
        )
        result.append(
            ElementProgressResponse(
                element_id=el.id,
                element_num=el.element_num,
                element_text=el.element_text,
                status=prog.status if prog else "not_started",
                attempts=prog.attempts if prog else 0,
                xp_awarded=prog.xp_awarded if prog else None,
                passed_at=prog.passed_at if prog else None,
            )
        )
    return UnitProgressResponse(unit_id=unit_id, elements=result)
