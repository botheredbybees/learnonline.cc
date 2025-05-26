"""
Assessments Router - Manages assessment and assessment question records in the system.

This module provides endpoints for:
- Creating, retrieving, updating and deleting assessments
- Managing assessment questions
- Retrieving assessment details for specific units
- Accessing assessment statistics and metrics

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from models.tables import Assessment, AssessmentQuestion
from models.schemas import AssessmentSchema, AssessmentQuestionSchema, AssessmentCreateSchema, AssessmentUpdateSchema, AssessmentQuestionCreateSchema, AssessmentQuestionUpdateSchema
from db.database import get_db

router = APIRouter(
    prefix="/assessments",
    tags=["assessments"],
    responses={404: {"description": "Assessment not found"}},
)


@router.get("/", response_model=List[AssessmentSchema])
async def get_all_assessments(
    skip: int = 0,
    limit: int = 100,
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all assessments with pagination support.
    
    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **unit_id**: Optional filter to get assessments for a specific unit
    
    Returns:
    - List of assessment objects with their details
    """
    if unit_id:
        assessments = db.query(Assessment).filter(Assessment.unit_id == unit_id).offset(skip).limit(limit).all()
    else:
        assessments = db.query(Assessment).offset(skip).limit(limit).all()
    
    return assessments


@router.get("/{assessment_id}", response_model=AssessmentSchema)
async def get_assessment_by_id(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific assessment by its ID.
    
    Parameters:
    - **assessment_id**: The unique identifier of the assessment
    
    Returns:
    - Assessment object with full details
    
    Raises:
    - 404: Assessment not found
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AssessmentSchema)
async def create_assessment(
    assessment_data: AssessmentCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new assessment.
    
    Parameters:
    - **assessment_data**: Assessment data including title, description, type and unit_id
    
    Returns:
    - Newly created assessment object
    
    Raises:
    - 400: Validation error
    """
    new_assessment = Assessment(**assessment_data.model_dump())
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    
    return new_assessment


@router.put("/{assessment_id}", response_model=AssessmentSchema)
async def update_assessment(
    assessment_id: int,
    assessment_data: AssessmentUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update an existing assessment.
    
    Parameters:
    - **assessment_id**: The ID of the assessment to update
    - **assessment_data**: Updated assessment data
    
    Returns:
    - Updated assessment object
    
    Raises:
    - 404: Assessment not found
    - 400: Validation error
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Convert Pydantic model to dict
    assessment_data_dict = assessment_data.model_dump(exclude_unset=True)
    for key, value in assessment_data_dict.items():
        setattr(assessment, key, value)
    
    db.commit()
    db.refresh(assessment)
    
    return assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an assessment.
    
    Parameters:
    - **assessment_id**: The ID of the assessment to delete
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Assessment not found
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    db.delete(assessment)
    db.commit()
    
    return None


# Assessment Questions Endpoints
@router.get("/{assessment_id}/questions", response_model=List[AssessmentQuestionSchema])
async def get_assessment_questions(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve all questions for a specific assessment.
    
    Parameters:
    - **assessment_id**: The ID of the assessment to get questions for
    
    Returns:
    - List of question objects
    
    Raises:
    - 404: Assessment not found
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.assessment_id == assessment_id
    ).all()
    
    return questions


@router.post("/{assessment_id}/questions", status_code=status.HTTP_201_CREATED, response_model=AssessmentQuestionSchema)
async def create_assessment_question(
    assessment_id: int,
    question_data: AssessmentQuestionCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new question for an assessment.
    
    Parameters:
    - **assessment_id**: The ID of the assessment to add a question to
    - **question_data**: Question data including text, type, and correct answer
    
    Returns:
    - Newly created question object
    
    Raises:
    - 404: Assessment not found
    - 400: Validation error
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Override assessment_id in the input data
    question_data_dict = question_data.model_dump()
    question_data_dict["assessment_id"] = assessment_id
    new_question = AssessmentQuestion(**question_data_dict)
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    return new_question


@router.get("/questions/{question_id}", response_model=AssessmentQuestionSchema)
async def get_question_by_id(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific question by its ID.
    
    Parameters:
    - **question_id**: The unique identifier of the question
    
    Returns:
    - Question object with full details
    
    Raises:
    - 404: Question not found
    """
    question = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.put("/questions/{question_id}", response_model=AssessmentQuestionSchema)
async def update_question(
    question_id: int,
    question_data: AssessmentQuestionUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update an existing question.
    
    Parameters:
    - **question_id**: The ID of the question to update
    - **question_data**: Updated question data
    
    Returns:
    - Updated question object
    
    Raises:
    - 404: Question not found
    - 400: Validation error
    """
    question = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Convert Pydantic model to dict
    question_data_dict = question_data.model_dump(exclude_unset=True)
    for key, value in question_data_dict.items():
        setattr(question, key, value)
    
    db.commit()
    db.refresh(question)
    
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a question.
    
    Parameters:
    - **question_id**: The ID of the question to delete
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Question not found
    """
    question = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    
    return None
