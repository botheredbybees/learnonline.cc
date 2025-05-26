import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..db.database import Base, get_db
from ..models.quiz import QuizQuestion, QuizAnswer, UserQuizAttempt
from ..models.quiz import QuizQuestionElement, QuizQuestionCriticalAspect

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_quiz.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

def test_create_question(client):
    response = client.post(
        "/api/quiz/questions/",
        json={
            "question_text": "What is Python?",
            "question_type": "MULTIPLE_CHOICE",
            "difficulty_level": 1,
            "experience_points": 10,
            "unit_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question_text"] == "What is Python?"
    assert data["id"] is not None

def test_get_questions_by_unit(client):
    # Create test question
    client.post(
        "/api/quiz/questions/",
        json={
            "question_text": "Test question",
            "question_type": "MULTIPLE_CHOICE",
            "difficulty_level": 1,
            "experience_points": 10,
            "unit_id": 1
        }
    )
    
    response = client.get("/api/quiz/unit/1/questions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["question_text"] == "Test question"

def test_link_question_to_element(client, session):
    # Create test question and element
    q = client.post(
        "/api/quiz/questions/",
        json={
            "question_text": "Test question",
            "question_type": "MULTIPLE_CHOICE",
            "difficulty_level": 1,
            "experience_points": 10,
            "unit_id": 1
        }
    ).json()
    
    # Create test element (simplified)
    element = UnitElement(element_num="1.1", element_text="Test element", unit_id=1)
    session.add(element)
    session.commit()
    
    response = client.post(f"/api/quiz/question/{q['id']}/link-element/{element.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Question successfully linked to element"
    
    # Verify relationship exists
    rel = session.query(QuizQuestionElement).filter_by(
        question_id=q["id"],
        element_id=element.id
    ).first()
    assert rel is not None

def test_get_questions_by_element(client, session):
    # Create test data
    q = client.post(
        "/api/quiz/questions/",
        json={
            "question_text": "Element question",
            "question_type": "MULTIPLE_CHOICE",
            "difficulty_level": 1,
            "experience_points": 10,
            "unit_id": 1
        }
    ).json()
    
    element = UnitElement(element_num="1.1", element_text="Test element", unit_id=1)
    session.add(element)
    session.commit()
    
    client.post(f"/api/quiz/question/{q['id']}/link-element/{element.id}")
    
    response = client.get(f"/api/quiz/element/{element.id}/questions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["question_text"] == "Element question"