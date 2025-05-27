"""
Download Manager Service - Handles bulk download operations for training data.

This service provides:
- Queue-based processing for bulk downloads
- Progress tracking and status management
- Error handling and recovery
- Integration with TGA client for data retrieval
"""

import os
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from db.database import SessionLocal
import models.tables as models
from services.tga.client import TrainingGovClient
from services.tga.exceptions import TGAClientError

logger = logging.getLogger(__name__)

class DownloadManager:
    """Manages bulk download operations for training packages and units"""
    
    def __init__(self):
        self.jobs = {}  # In production, use Redis or database
        
    def create_job(self, job_type: str, items: List[str], user_id: int) -> str:
        """Create a new download job"""
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "id": job_id,
            "type": job_type,
            "status": "queued",
            "user_id": user_id,
            "total_items": len(items),
            "completed_items": 0,
            "failed_items": 0,
            "current_item": None,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "errors": [],
            "items": items,
            "results": []
        }
        
        logger.info(f"Created download job {job_id} for {len(items)} {job_type}")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a download job"""
        return self.jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: str, **kwargs):
        """Update job status and additional fields"""
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            for key, value in kwargs.items():
                self.jobs[job_id][key] = value
    
    def process_training_package_download(self, job_id: str, package_codes: List[str], user_id: int):
        """Process bulk download of training packages"""
        logger.info(f"Starting training package download job {job_id}")
        
        # Update job status
        self.update_job_status(job_id, "processing")
        
        # Create new database session for background task
        db = SessionLocal()
        
        try:
            # Get TGA credentials
            username = os.getenv("TGA_USERNAME")
            password = os.getenv("TGA_PASSWORD")
            
            if not username or not password:
                self.update_job_status(
                    job_id, 
                    "failed",
                    errors=["TGA API credentials not configured"]
                )
                return
            
            client = TrainingGovClient(username=username, password=password)
            
            for package_code in package_codes:
                try:
                    # Update current package being processed
                    self.update_job_status(job_id, "processing", current_item=package_code)
                    
                    # Get package details from TGA
                    package_data = client.get_component_details(package_code)
                    
                    if not package_data or not isinstance(package_data, dict):
                        self.jobs[job_id]["failed_items"] += 1
                        self.jobs[job_id]["errors"].append(f"Package {package_code} not found in TGA")
                        continue
                    
                    # Store or update package in database
                    package = self._store_training_package(db, package_data)
                    
                    # Queue units download for this package
                    self._queue_units_download(db, client, package, job_id)
                    
                    self.jobs[job_id]["completed_items"] += 1
                    self.jobs[job_id]["results"].append({
                        "code": package_code,
                        "status": "success",
                        "package_id": package.id if package else None
                    })
                    
                    logger.info(f"Successfully processed package {package_code}")
                    
                except Exception as e:
                    self.jobs[job_id]["failed_items"] += 1
                    error_msg = f"Error processing {package_code}: {str(e)}"
                    self.jobs[job_id]["errors"].append(error_msg)
                    self.jobs[job_id]["results"].append({
                        "code": package_code,
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(error_msg)
                    db.rollback()
            
            # Mark job as completed
            self.update_job_status(
                job_id,
                "completed",
                completed_at=datetime.now().isoformat(),
                current_item=None
            )
            
            logger.info(f"Completed training package download job {job_id}")
            
        except Exception as e:
            error_msg = f"Bulk download failed: {str(e)}"
            self.update_job_status(
                job_id,
                "failed",
                errors=[error_msg]
            )
            logger.error(error_msg)
        finally:
            db.close()
    
    def process_units_download(self, job_id: str, unit_codes: List[str], user_id: int):
        """Process bulk download of units with full data population"""
        logger.info(f"Starting units download job {job_id}")
        
        # Update job status
        self.update_job_status(job_id, "processing")
        
        # Create new database session for background task
        db = SessionLocal()
        
        try:
            # Get TGA credentials
            username = os.getenv("TGA_USERNAME")
            password = os.getenv("TGA_PASSWORD")
            
            if not username or not password:
                self.update_job_status(
                    job_id,
                    "failed", 
                    errors=["TGA API credentials not configured"]
                )
                return
            
            client = TrainingGovClient(username=username, password=password)
            
            for unit_code in unit_codes:
                try:
                    # Update current unit being processed
                    self.update_job_status(job_id, "processing", current_item=unit_code)
                    
                    # Get unit details from TGA
                    unit_data = client.get_component_details(unit_code)
                    
                    if not unit_data or not isinstance(unit_data, dict):
                        self.jobs[job_id]["failed_items"] += 1
                        self.jobs[job_id]["errors"].append(f"Unit {unit_code} not found in TGA")
                        continue
                    
                    # Store or update unit in database
                    unit = self._store_unit(db, unit_data)
                    
                    # Process unit XML for comprehensive data population
                    self._process_unit_xml(db, client, unit, job_id)
                    
                    self.jobs[job_id]["completed_items"] += 1
                    self.jobs[job_id]["results"].append({
                        "code": unit_code,
                        "status": "success",
                        "unit_id": unit.id if unit else None
                    })
                    
                    logger.info(f"Successfully processed unit {unit_code}")
                    
                except Exception as e:
                    self.jobs[job_id]["failed_items"] += 1
                    error_msg = f"Error processing {unit_code}: {str(e)}"
                    self.jobs[job_id]["errors"].append(error_msg)
                    self.jobs[job_id]["results"].append({
                        "code": unit_code,
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(error_msg)
                    db.rollback()
            
            # Mark job as completed
            self.update_job_status(
                job_id,
                "completed",
                completed_at=datetime.now().isoformat(),
                current_item=None
            )
            
            logger.info(f"Completed units download job {job_id}")
            
        except Exception as e:
            error_msg = f"Units bulk download failed: {str(e)}"
            self.update_job_status(
                job_id,
                "failed",
                errors=[error_msg]
            )
            logger.error(error_msg)
        finally:
            db.close()
    
    def _store_training_package(self, db: Session, package_data: Dict[str, Any]) -> models.TrainingPackage:
        """Store or update training package in database"""
        package = db.query(models.TrainingPackage).filter(
            models.TrainingPackage.code == package_data["code"]
        ).first()
        
        if package:
            # Update existing package
            updates = {}
            if "title" in package_data and package_data.get("title") is not None:
                updates["title"] = package_data["title"]
            if "description" in package_data and package_data.get("description") is not None:
                updates["description"] = package_data.get("description")
            if "status" in package_data and package_data.get("status") is not None:
                updates["status"] = package_data.get("status")
            if "release_date" in package_data and package_data.get("release_date") is not None:
                updates["release_date"] = package_data.get("release_date")
            if "xml_file" in package_data and package_data.get("xml_file") is not None:
                updates["xml_file"] = package_data.get("xml_file")
            
            updates["processed"] = "N"  # Mark for reprocessing
            
            # Update using direct attribute assignment
            for key, value in updates.items():
                setattr(package, key, value)
        else:
            # Create new package
            new_package_data = {
                "code": package_data["code"],
                "title": package_data["title"],
                "processed": "N"
            }
            
            if "description" in package_data and package_data.get("description") is not None:
                new_package_data["description"] = package_data.get("description")
            if "status" in package_data and package_data.get("status") is not None:
                new_package_data["status"] = package_data.get("status")
            if "release_date" in package_data and package_data.get("release_date") is not None:
                new_package_data["release_date"] = package_data.get("release_date")
            if "xml_file" in package_data and package_data.get("xml_file") is not None:
                new_package_data["xml_file"] = package_data.get("xml_file")
                
            package = models.TrainingPackage(**new_package_data)
            db.add(package)
        
        db.commit()
        db.refresh(package)
        return package
    
    def _store_unit(self, db: Session, unit_data: Dict[str, Any]) -> models.Unit:
        """Store or update unit in database"""
        unit = db.query(models.Unit).filter(
            models.Unit.code == unit_data["code"]
        ).first()
        
        if unit:
            # Update existing unit
            updates = {}
            if "title" in unit_data and unit_data.get("title") is not None:
                updates["title"] = unit_data["title"]
            if "description" in unit_data and unit_data.get("description") is not None:
                updates["description"] = unit_data.get("description")
            if "status" in unit_data and unit_data.get("status") is not None:
                updates["status"] = unit_data.get("status")
            if "release_date" in unit_data and unit_data.get("release_date") is not None:
                updates["release_date"] = unit_data.get("release_date")
            if "xml_file" in unit_data and unit_data.get("xml_file") is not None:
                updates["xml_file"] = unit_data.get("xml_file")
            
            updates["processed"] = "N"  # Mark for reprocessing
            
            # Update using direct attribute assignment
            for key, value in updates.items():
                setattr(unit, key, value)
        else:
            # Create new unit
            new_unit_data = {
                "code": unit_data["code"],
                "title": unit_data["title"],
                "processed": "N"
            }
            
            if "description" in unit_data and unit_data.get("description") is not None:
                new_unit_data["description"] = unit_data.get("description")
            if "status" in unit_data and unit_data.get("status") is not None:
                new_unit_data["status"] = unit_data.get("status")
            if "release_date" in unit_data and unit_data.get("release_date") is not None:
                new_unit_data["release_date"] = unit_data.get("release_date")
            if "xml_file" in unit_data and unit_data.get("xml_file") is not None:
                new_unit_data["xml_file"] = unit_data.get("xml_file")
                
            unit = models.Unit(**new_unit_data)
            db.add(unit)
        
        db.commit()
        db.refresh(unit)
        return unit
    
    def _queue_units_download(self, db: Session, client: TrainingGovClient, package: models.TrainingPackage, job_id: str):
        """Queue units download for a training package"""
        try:
            # Search for units in this training package
            component_types = {
                'IncludeAccreditedCourse': False,
                'IncludeAccreditedCourseModule': False,
                'IncludeQualification': False,
                'IncludeSkillSet': False,
                'IncludeTrainingPackage': False,
                'IncludeUnit': True,
                'IncludeUnitContextualisation': False
            }
            
            # Search for units with training package code prefix
            result = client.search_components(
                filter_text=package.code,
                component_types=component_types,
                page=1,
                page_size=500  # Large page size to get all units
            )
            
            units = result.get('components', [])
            
            # Store basic unit information
            for unit_data in units:
                if unit_data["code"].startswith(package.code):
                    self._store_unit(db, unit_data)
            
            logger.info(f"Queued {len(units)} units for package {package.code}")
            
        except Exception as e:
            logger.error(f"Error queuing units for package {package.code}: {str(e)}")
    
    def _process_unit_xml(self, db: Session, client: TrainingGovClient, unit: models.Unit, job_id: str):
        """Process unit XML to populate all related tables"""
        try:
            # Get XML content for the unit
            xml_data = client.get_component_xml(unit.code)
            
            if not xml_data or "xml" not in xml_data:
                logger.warning(f"No XML data found for unit {unit.code}")
                return
            
            # Parse elements and performance criteria (existing functionality)
            elements = client.extract_elements(xml_data["xml"])
            
            if elements:
                # Clear existing elements and performance criteria
                db.query(models.UnitPerformanceCriteria).filter(
                    models.UnitPerformanceCriteria.unit_id == unit.id
                ).delete()
                
                db.query(models.UnitElement).filter(
                    models.UnitElement.unit_id == unit.id
                ).delete()
                
                # Insert new elements and performance criteria
                for element_data in elements:
                    element = models.UnitElement(
                        unit_id=unit.id,
                        element_num=str(element_data.get("number", "")),
                        element_text=str(element_data.get("title", ""))
                    )
                    db.add(element)
                    db.flush()  # Flush to get the ID
                    
                    # Insert performance criteria
                    for pc_data in element_data.get("performance_criteria", []):
                        pc = models.UnitPerformanceCriteria(
                            element_id=element.id,
                            unit_id=unit.id,
                            pc_num=str(pc_data.get("number", "")),
                            pc_text=str(pc_data.get("text", ""))
                        )
                        db.add(pc)
            
            # TODO: Parse and populate critical aspects, required skills, qualifications, skillsets
            # This will be implemented in Phase 3
            
            # Mark unit as processed
            setattr(unit, "processed", "Y")
            db.commit()
            
            logger.info(f"Successfully processed XML for unit {unit.code}")
            
        except Exception as e:
            logger.error(f"Error processing XML for unit {unit.code}: {str(e)}")
            db.rollback()

# Global instance
download_manager = DownloadManager()
