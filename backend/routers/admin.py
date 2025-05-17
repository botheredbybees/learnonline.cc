from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import subprocess
import shlex
import sys
import os
from datetime import datetime

from sqlalchemy.orm import Session
from db.database import get_db
from models.user import User
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

@router.get("/training-packages", dependencies=[Depends(JWTBearer())])
async def get_training_packages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all training packages"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin features")
        
    # Get training packages from database
    training_packages = db.execute("""
        SELECT 
            id, code, title, status, release_date, 
            last_checked, created_at, updated_at
        FROM training_packages
        ORDER BY code
    """).fetchall()
    
    return {"training_packages": [dict(tp) for tp in training_packages]}

@router.post("/sync-training-packages", dependencies=[Depends(JWTBearer())])
async def sync_training_packages(
    background_tasks: BackgroundTasks,
    tp_codes: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync training packages from TGA"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin features")
    
    # Record the sync task in the database
    task_id = db.execute("""
        INSERT INTO admin_tasks (task_type, created_by, status, params)
        VALUES ('sync_tga', %s, 'pending', %s)
        RETURNING id
    """, (str(current_user.id), str(tp_codes) if tp_codes else None)).fetchone()[0]
    
    db.commit()
    
    # Launch tp_get.py as a background task
    def run_tp_get():
        try:
            cmd = [sys.executable, os.path.join(os.getcwd(), "..", "tp_get.py")]
            if tp_codes:
                cmd.extend(["--tp-codes"] + tp_codes)
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            success = result.returncode == 0
            
            # Update task status
            with db.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE admin_tasks
                        SET status = %s, 
                            completed_at = %s, 
                            result = %s
                        WHERE id = %s
                    """, (
                        'completed' if success else 'failed',
                        datetime.now(),
                        result.stdout if success else result.stderr,
                        task_id
                    ))
                    conn.commit()
        except Exception as e:
            # Log error and update task status
            with db.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE admin_tasks
                        SET status = 'failed', 
                            completed_at = %s, 
                            result = %s
                        WHERE id = %s
                    """, (datetime.now(), str(e), task_id))
                    conn.commit()
    
    background_tasks.add_task(run_tp_get)
    
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Training package sync started",
            "task_id": task_id
        }
    )

@router.get("/tasks", dependencies=[Depends(JWTBearer())])
async def get_admin_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get admin tasks"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin features")
        
    # Get tasks from database
    tasks = db.execute("""
        SELECT 
            id, task_type, status, created_at, completed_at,
            params, result
        FROM admin_tasks
        ORDER BY created_at DESC
        LIMIT 50
    """).fetchall()
    
    return {"tasks": [dict(task) for task in tasks]}

@router.get("/tasks/{task_id}", dependencies=[Depends(JWTBearer())])
async def get_admin_task(
    task_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get a specific admin task"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin features")
        
    # Get task from database
    task = db.execute("""
        SELECT 
            id, task_type, status, created_at, completed_at,
            params, result
        FROM admin_tasks
        WHERE id = %s
    """, (task_id,)).fetchone()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"task": dict(task)}
