from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routers
from routers import (
    auth,
    users,
    roles,
    permissions,
    units,
    training_packages,
    qualifications,
    skillsets,
    assessments,
    user_progress,
    achievements,
    badges,
    gamification,
)
from routers.quiz import router as quiz_router

# Load environment variables
load_dotenv()

# Create the database tables (only in non-test environments)
if os.getenv("ENVIRONMENT") != "test":
    from database import engine
    import models.tables as models

    models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LearnOnline API",
    description="Backend API for LearnOnline platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint for health checks
@app.get("/")
async def health_check():
    return {"status": "healthy"}


@app.get("/api")
async def api_ready():
    return {"status": "ready"}


# Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(units.router)
app.include_router(training_packages.router)
app.include_router(qualifications.router)
app.include_router(skillsets.router)
app.include_router(assessments.router)
app.include_router(user_progress.router)
app.include_router(achievements.router)
app.include_router(badges.router)
app.include_router(gamification.router)
app.include_router(quiz_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
