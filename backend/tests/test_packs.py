"""Tests for M2 pack import and admin question management."""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.tables import User, Role, UserProfile, Unit, TrainingPackage
from auth.auth_handler import get_password_hash, sign_jwt

SAMPLE_PACK = {
    "training_package": "TST",
    "training_package_title": "Test Package",
    "generated_at": "2026-05-18",
    "model": "qwen2.5:14b",
    "qualifications": [],
    "units": [
        {
            "code": f"TSTXX{uuid.uuid4().hex[:4].upper()}",
            "title": "Test Unit One",
            "description": "A test unit",
            "plain_english_description": "Plain English description here.",
            "elements": [
                {
                    "code": "01",
                    "title": "First element",
                    "performance_criteria": [
                        {"code": "01.01", "text": "Do the first thing"}
                    ],
                    "critical_aspects": [{"text": "Know the first thing"}],
                    "questions": [
                        {
                            "pc_code": "01.01",
                            "question_type": "mcq",
                            "question_text": "What is the first thing?",
                            "options": {
                                "choices": ["A", "B", "C", "D"],
                                "correct": 0,
                                "explanation": "A is correct.",
                            },
                            "source": "ai_generated",
                            "review_status": "draft",
                        }
                    ],
                }
            ],
        }
    ],
}


@pytest.fixture
def admin_token(db: Session):
    role = Role(name=f"admin-{uuid.uuid4().hex[:6]}", description="Admin")
    db.add(role)
    db.flush()
    user = User(
        email=f"admin-{uuid.uuid4().hex[:6]}@test.com",
        password_hash=get_password_hash("password"),
        role_id=role.id,
    )
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id, experience_points=0))
    db.commit()
    return sign_jwt(str(user.id), "admin")["access_token"]


class TestPackImport:
    def test_import_pack_creates_unit_and_questions(
        self, client: TestClient, admin_token, db: Session
    ):
        pack = dict(SAMPLE_PACK)
        pack["units"] = [
            {**SAMPLE_PACK["units"][0], "code": f"TSTYY{uuid.uuid4().hex[:4].upper()}"}
        ]
        resp = client.post(
            "/api/admin/packs/import",
            json={"pack_data": pack},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["training_package_code"] == "TST"
        assert data["question_count"] == 1
        assert data["status"] == "imported"

    def test_imported_questions_are_draft(
        self, client: TestClient, admin_token, db: Session
    ):
        pack = dict(SAMPLE_PACK)
        pack["units"] = [
            {**SAMPLE_PACK["units"][0], "code": f"TSTZZ{uuid.uuid4().hex[:4].upper()}"}
        ]
        client.post(
            "/api/admin/packs/import",
            json={"pack_data": pack},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        resp = client.get(
            "/api/admin/questions?review_status=draft",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        questions = resp.json()
        assert len(questions) >= 1
        assert all(q["review_status"] == "draft" for q in questions)


class TestQuestionAdmin:
    def test_approve_question(self, client: TestClient, admin_token, db: Session):
        pack = dict(SAMPLE_PACK)
        pack["units"] = [
            {**SAMPLE_PACK["units"][0], "code": f"TSTAA{uuid.uuid4().hex[:4].upper()}"}
        ]
        client.post(
            "/api/admin/packs/import",
            json={"pack_data": pack},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        questions_resp = client.get(
            "/api/admin/questions?review_status=draft",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        qid = questions_resp.json()[0]["id"]

        resp = client.patch(
            f"/api/admin/questions/{qid}",
            json={"review_status": "approved", "is_active": True},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["review_status"] == "approved"
