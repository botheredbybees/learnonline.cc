from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LearnOnline API",
    description="Backend API for LearnOnline platform",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to LearnOnline API", "status": "healthy"}

# Import and include routers
# from routers import users, courses, auth
# app.include_router(auth.router)
# app.include_router(users.router)
# app.include_router(courses.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 