"""Admin endpoints for pack import and question management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from auth.auth_bearer import JWTBearer
import models.tables as models
from models.schemas import PackImportResponse, QuestionAdminItem, QuestionPatchRequest

router = APIRouter(prefix="/api/admin", tags=["admin-packs"])


def _upsert_unit(db: Session, unit_data: dict) -> models.Unit:
    unit = db.query(models.Unit).filter_by(code=unit_data["code"]).first()
    if unit is None:
        unit = models.Unit(
            code=unit_data["code"],
            title=unit_data["title"],
            description=unit_data.get("description", ""),
        )
        db.add(unit)
        db.flush()
    unit.plain_english_description = unit_data.get("plain_english_description")
    db.flush()
    return unit


def _upsert_element(
    db: Session, element_data: dict, unit: models.Unit
) -> models.UnitElement:
    element = (
        db.query(models.UnitElement)
        .filter_by(unit_id=unit.id, element_num=element_data["code"])
        .first()
    )
    if element is None:
        element = models.UnitElement(
            unit_id=unit.id,
            element_num=element_data["code"],
            element_text=element_data["title"],
        )
        db.add(element)
        db.flush()
    return element


def _upsert_assessment(
    db: Session, element: models.UnitElement, unit: models.Unit
) -> models.Assessment:
    assessment = db.query(models.Assessment).filter_by(element_id=element.id).first()
    if assessment is None:
        assessment = models.Assessment(
            unit_id=unit.id,
            element_id=element.id,
            title=f"{unit.code} — {element.element_text}",
            type="quiz",
            experience_points=50,
        )
        db.add(assessment)
        db.flush()
    return assessment


def _upsert_pc(
    db: Session,
    pc_data: dict,
    element: models.UnitElement,
    unit: models.Unit,
) -> models.UnitPerformanceCriteria:
    pc = (
        db.query(models.UnitPerformanceCriteria)
        .filter_by(element_id=element.id, pc_num=pc_data["code"])
        .first()
    )
    if pc is None:
        pc = models.UnitPerformanceCriteria(
            element_id=element.id,
            unit_id=unit.id,
            pc_num=pc_data["code"],
            pc_text=pc_data["text"],
        )
        db.add(pc)
        db.flush()
    return pc


@router.post("/packs/import", dependencies=[Depends(JWTBearer())])
def import_pack(payload: dict, db: Session = Depends(get_db)) -> PackImportResponse:
    """
    Import a question pack JSON. Upserts unit structure and questions.
    All questions imported with review_status='draft', is_active=False.
    """
    pack_data = payload.get("pack_data")
    if not pack_data:
        raise HTTPException(status_code=400, detail="pack_data required")

    tp_code = pack_data.get("training_package", "UNKNOWN")
    total_questions = 0

    pack_record = models.QuestionPack(
        training_package_code=tp_code,
        source_url=pack_data.get("source_url", ""),
        version=pack_data.get("generated_at", ""),
        status="pending",
    )
    db.add(pack_record)
    db.flush()

    unit_count = 0
    for unit_data in pack_data.get("units", []):
        unit = _upsert_unit(db, unit_data)
        unit_count += 1

        for element_data in unit_data.get("elements", []):
            element = _upsert_element(db, element_data, unit)
            assessment = _upsert_assessment(db, element, unit)

            pc_map = {}
            for pc_data in element_data.get("performance_criteria", []):
                pc = _upsert_pc(db, pc_data, element, unit)
                pc_map[pc_data["code"]] = pc.id

            for q_data in element_data.get("questions", []):
                q = models.AssessmentQuestion(
                    assessment_id=assessment.id,
                    pc_id=pc_map.get(q_data.get("pc_code")),
                    question_text=q_data["question_text"],
                    question_type=q_data["question_type"],
                    options=q_data.get("options", {}),
                    source=q_data.get("source", "ai_generated"),
                    review_status="draft",
                    is_active=False,
                )
                db.add(q)
                total_questions += 1

    pack_record.question_count = total_questions
    pack_record.status = "imported"
    pack_record.imported_at = datetime.now(timezone.utc)
    db.commit()

    return PackImportResponse(
        pack_id=pack_record.id,
        training_package_code=tp_code,
        unit_count=unit_count,
        question_count=total_questions,
        status="imported",
    )


@router.get("/questions", dependencies=[Depends(JWTBearer())])
def list_questions(
    review_status: Optional[str] = Query(None),
    unit_code: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
) -> List[QuestionAdminItem]:
    query = db.query(models.AssessmentQuestion)
    if review_status:
        query = query.filter(models.AssessmentQuestion.review_status == review_status)
    if question_type:
        query = query.filter(models.AssessmentQuestion.question_type == question_type)
    questions = query.offset(skip).limit(limit).all()
    return [
        QuestionAdminItem(
            id=q.id,
            assessment_id=q.assessment_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options or {},
            source=q.source,
            review_status=q.review_status,
            is_active=q.is_active,
        )
        for q in questions
    ]


@router.patch("/questions/{question_id}", dependencies=[Depends(JWTBearer())])
def patch_question(
    question_id: int,
    payload: QuestionPatchRequest,
    db: Session = Depends(get_db),
) -> QuestionAdminItem:
    q = db.query(models.AssessmentQuestion).filter_by(id=question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    if payload.question_text is not None:
        q.question_text = payload.question_text
    if payload.options is not None:
        q.options = payload.options
    if payload.review_status is not None:
        q.review_status = payload.review_status
    if payload.is_active is not None:
        q.is_active = payload.is_active
    db.commit()
    db.refresh(q)
    return QuestionAdminItem(
        id=q.id,
        assessment_id=q.assessment_id,
        question_text=q.question_text,
        question_type=q.question_type,
        options=q.options or {},
        source=q.source,
        review_status=q.review_status,
        is_active=q.is_active,
    )


@router.get("/progress", dependencies=[Depends(JWTBearer())])
def get_class_progress(
    unit_id: int = Query(...),
    db: Session = Depends(get_db),
):
    unit = db.query(models.Unit).filter_by(id=unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    elements = (
        db.query(models.UnitElement)
        .filter_by(unit_id=unit_id)
        .order_by(models.UnitElement.element_num)
        .all()
    )
    element_ids = [e.id for e in elements]

    all_progress = (
        db.query(models.UserElementProgress)
        .filter(models.UserElementProgress.element_id.in_(element_ids))
        .all()
    )

    students = {}
    for p in all_progress:
        if p.user_id not in students:
            user = db.query(models.User).filter_by(id=p.user_id).first()
            students[p.user_id] = {
                "student_id": p.user_id,
                "email": user.email if user else "",
                "elements": {},
            }
        students[p.user_id]["elements"][p.element_id] = p.status

    return {
        "unit_id": unit_id,
        "elements": [
            {
                "element_id": e.id,
                "element_num": e.element_num,
                "element_text": e.element_text,
            }
            for e in elements
        ],
        "students": list(students.values()),
    }
