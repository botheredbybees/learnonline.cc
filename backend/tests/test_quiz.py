"""Tests for M2 quiz endpoints."""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.tables import (
    Unit,
    UnitElement,
    Assessment,
    AssessmentQuestion,
    UserElementProgress,
    UserAnswer,
    User,
    UserProfile,
    Role,
)
from auth.auth_handler import get_password_hash, sign_jwt


@pytest.fixture
def quiz_data(db: Session):
    """Create a unit with one element and two MCQ questions."""
    role = Role(name=f"student-{uuid.uuid4().hex[:6]}", description="Student")
    db.add(role)
    db.flush()

    user = User(
        email=f"student-{uuid.uuid4().hex[:6]}@test.com",
        password_hash=get_password_hash("password"),
        role_id=role.id,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(user_id=user.id, experience_points=0)
    db.add(profile)

    unit = Unit(
        code=f"TST{uuid.uuid4().hex[:4].upper()}",
        title="Test Unit",
        experience_points=100,
    )
    db.add(unit)
    db.flush()

    element = UnitElement(
        unit_id=unit.id, element_num="01", element_text="Do the thing"
    )
    db.add(element)
    db.flush()

    assessment = Assessment(
        unit_id=unit.id,
        element_id=element.id,
        title="Element 01 Quiz",
        type="quiz",
        experience_points=50,
    )
    db.add(assessment)
    db.flush()

    q1 = AssessmentQuestion(
        assessment_id=assessment.id,
        question_text="Which PPE is required?",
        question_type="mcq",
        options={
            "choices": ["None", "Gloves", "Respirator", "All of above"],
            "correct": 3,
            "explanation": "All PPE required.",
        },
        source="teacher",
        review_status="approved",
        is_active=True,
    )
    q2 = AssessmentQuestion(
        assessment_id=assessment.id,
        question_text="What is the standard width?",
        question_type="mcq",
        options={
            "choices": ["900mm", "1200mm", "600mm", "Any width"],
            "correct": 1,
            "explanation": "1200mm is standard.",
        },
        source="teacher",
        review_status="approved",
        is_active=True,
    )
    db.add_all([q1, q2])
    db.commit()
    db.refresh(q1)
    db.refresh(q2)

    token = sign_jwt(str(user.id), "student")["access_token"]
    return {
        "user": user,
        "unit": unit,
        "element": element,
        "questions": [q1, q2],
        "token": token,
    }


class TestQuizState:
    def test_get_quiz_state_returns_elements(self, client: TestClient, quiz_data):
        resp = client.get(
            f"/api/quiz/units/{quiz_data['unit'].id}/quiz-state",
            headers={"Authorization": f"Bearer {quiz_data['token']}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["unit_id"] == quiz_data["unit"].id
        assert len(data["elements"]) == 1
        assert data["elements"][0]["status"] == "not_started"

    def test_get_element_questions_returns_active_approved(
        self, client: TestClient, quiz_data
    ):
        resp = client.get(
            f"/api/quiz/elements/{quiz_data['element'].id}/questions",
            headers={"Authorization": f"Bearer {quiz_data['token']}"},
        )
        assert resp.status_code == 200
        questions = resp.json()
        assert len(questions) == 2
        assert all(q["question_type"] == "mcq" for q in questions)


class TestAnswerSubmission:
    def test_correct_answer_returns_is_correct_true(
        self, client: TestClient, quiz_data, db: Session
    ):
        session_id = str(uuid.uuid4())
        q = quiz_data["questions"][0]
        resp = client.post(
            "/api/quiz/answer",
            json={
                "question_id": q.id,
                "element_id": quiz_data["element"].id,
                "session_id": session_id,
                "answer": {"selected": 3},
            },
            headers={"Authorization": f"Bearer {quiz_data['token']}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_correct"] is True

    def test_wrong_answer_returns_is_correct_false(
        self, client: TestClient, quiz_data, db: Session
    ):
        session_id = str(uuid.uuid4())
        q = quiz_data["questions"][0]
        resp = client.post(
            "/api/quiz/answer",
            json={
                "question_id": q.id,
                "element_id": quiz_data["element"].id,
                "session_id": session_id,
                "answer": {"selected": 0},
            },
            headers={"Authorization": f"Bearer {quiz_data['token']}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_correct"] is False

    def test_all_correct_passes_element_and_awards_xp(
        self, client: TestClient, quiz_data, db: Session
    ):
        session_id = str(uuid.uuid4())
        questions = quiz_data["questions"]
        token = quiz_data["token"]
        element_id = quiz_data["element"].id

        for q in questions:
            correct_idx = q.options["correct"]
            client.post(
                "/api/quiz/answer",
                json={
                    "question_id": q.id,
                    "element_id": element_id,
                    "session_id": session_id,
                    "answer": {"selected": correct_idx},
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        prog = (
            db.query(UserElementProgress)
            .filter_by(user_id=quiz_data["user"].id, element_id=element_id)
            .first()
        )
        assert prog is not None
        assert prog.status == "passed"
        assert prog.xp_awarded == 50

        from models.tables import UserProfile

        profile = db.query(UserProfile).filter_by(user_id=quiz_data["user"].id).first()
        db.refresh(profile)
        assert profile.experience_points >= 50
