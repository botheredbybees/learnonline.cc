from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

# Import routers
from routers import admin, auth, units, users

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LearnOnline API",
    description="Backend API for LearnOnline platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(units.router, prefix="/api")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to LearnOnline API", "status": "healthy"}

# Import and include routers
from routers import users, auth, admin, units
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(units.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 