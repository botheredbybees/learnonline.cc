from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

# Import routers
from routers import admin, auth, units, users, quests, favorites, public

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
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for health checks
@app.get("/")
async def root():
    return {"status": "ok", "message": "LearnOnline API is running"}

@app.get("/api")
async def api_root():
    return {"status": "ok", "message": "LearnOnline API is ready"}

# Root endpoint for health checks
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "LearnOnline API is running"}

@app.get("/api")
async def api_ready():
    return {"status": "ok", "message": "LearnOnline API is ready"}

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(units.router, prefix="/api")
app.include_router(quests.router, prefix="/api")
app.include_router(favorites.router, prefix="/api")
app.include_router(public.router, prefix="/api")  # Public routes without authentication

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to LearnOnline API", "status": "healthy"}
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(units.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 