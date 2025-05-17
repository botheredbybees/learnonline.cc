from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import subprocess
import os
import json
from datetime import datetime
import psycopg2
import sys

from sqlalchemy.orm import Session
from sqlalchemy import text
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
    stmt = text("""
        SELECT 
            id, code, title, status, release_date, 
            last_checked, created_at, updated_at
        FROM training_packages
        ORDER BY code
    """)
    result = db.execute(stmt)
    training_packages = result.fetchall()
    
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
    stmt = text("""
        INSERT INTO admin_tasks (task_type, created_by, status, params)
        VALUES (:task_type, :created_by, :status, :params)
        RETURNING id
    """)
    params = {
        "task_type": "sync_tga",
        "created_by": str(current_user.id),
        "status": "pending",
        "params": json.dumps(tp_codes) if tp_codes else None
    }
    result = db.execute(stmt, params)
    task_id = result.scalar_one()
    
    db.commit()
    
    # Launch tp_get.py as a background task
    def run_tp_get():
        try:
            script_path = os.path.join(os.getcwd(), "backend", "scripts", "tga", "tp_get.py")
            cmd = [sys.executable, script_path]
            if tp_codes:
                cmd.extend(["--tp-codes"] + tp_codes)
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            success = result.returncode == 0
            
            # Update task status using direct psycopg2 connection
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5332')
            )
            
            with conn:
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
        except Exception as e:
            # Log error and update task status
            try:
                conn = psycopg2.connect(
                    dbname=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=os.getenv('DB_PORT', '5332')
                )
                
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE admin_tasks
                            SET status = %s, 
                                completed_at = %s, 
                                result = %s
                            WHERE id = %s
                        """, (
                            'failed',
                            datetime.now(), 
                            str(e), 
                            task_id
                        ))
            except:
                pass
    
    background_tasks.add_task(run_tp_get)
    
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Training package sync started",
            "task_id": task_id
        }
    )

@router.post("/process-unit-elements", dependencies=[Depends(JWTBearer())])
async def process_unit_elements(
    background_tasks: BackgroundTasks,
    unit_id: Optional[int] = None,
    unit_code: Optional[str] = None,
    use_local_files: Optional[bool] = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process unit elements and performance criteria from XML
    
    If unit_id or unit_code is provided, only process that specific unit.
    If use_local_files is True, try to process XML files from the local directory.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin features")
    
    # Record the task in the database
    stmt = text("""
        INSERT INTO admin_tasks (task_type, created_by, status, params)
        VALUES (:task_type, :created_by, :status, :params)
        RETURNING id
    """)
    
    params_data = {
        "unit_id": unit_id,
        "unit_code": unit_code,
        "use_local_files": use_local_files
    }
    
    query_params = {
        "task_type": "process_elements",
        "created_by": str(current_user.id),
        "status": "pending",
        "params": json.dumps(params_data)
    }
    
    result = db.execute(stmt, query_params)
    task_id = result.scalar_one()
    
    db.commit()
    
    # Launch tp_get.py as a background task
    def run_process_elements():
        try:
            script_path = os.path.join(os.getcwd(), "backend", "scripts", "tga", "tp_get.py")
            
            if use_local_files:
                # Process local XML files
                cmd = [
                    sys.executable, 
                    script_path, 
                    "--process-local"
                ]
                
                if unit_code:
                    # We'll need to implement this in the script 
                    cmd.extend(["--unit-code", unit_code])
            else:
                # Process using TGA API
                cmd = [
                    sys.executable, 
                    script_path, 
                    "--process-existing"
                ]
                
                if unit_id:
                    cmd.extend(["--unit-id", str(unit_id)])
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            success = result.returncode == 0
            
            # Update task status
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5332')
            )
            
            with conn:
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
        except Exception as e:
            # Log error and update task status
            try:
                conn = psycopg2.connect(
                    dbname=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=os.getenv('DB_PORT', '5332')
                )
                
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE admin_tasks
                            SET status = %s, 
                                completed_at = %s, 
                                result = %s
                            WHERE id = %s
                        """, (
                            'failed',
                            datetime.now(), 
                            str(e), 
                            task_id
                        ))
            except:
                pass
    
    background_tasks.add_task(run_process_elements)
    
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Unit elements processing started",
            "task_id": task_id
        }
    )

@router.get("/tasks", dependencies=[Depends(JWTBearer())])
async def get_admin_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get admin tasks"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin features")
        
    # Get tasks from database
    stmt = text("""
        SELECT 
            id, task_type, status, created_at, completed_at,
            params, result
        FROM admin_tasks
        ORDER BY created_at DESC
        LIMIT 50
    """)
    result = db.execute(stmt)
    tasks = result.fetchall()
    
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
    stmt = text("""
        SELECT 
            id, task_type, status, created_at, completed_at,
            params, result
        FROM admin_tasks
        WHERE id = :task_id
    """)
    result = db.execute(stmt, {"task_id": task_id})
    task = result.fetchone()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"task": dict(task)}
