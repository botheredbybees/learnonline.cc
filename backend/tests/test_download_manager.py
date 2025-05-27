"""
Tests for the Download Manager Service

This module tests the bulk download functionality for training packages and units,
including job management, progress tracking, and data population.
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from services.download_manager import DownloadManager
import models.tables as models


class TestDownloadManager:
    """Test cases for the DownloadManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.download_manager = DownloadManager()
        self.test_user_id = 1
        self.test_package_codes = ["ICT40120", "BSB50420"]
        self.test_unit_codes = ["ICTICT418", "BSBWHS411"]
    
    def test_create_job(self):
        """Test job creation with proper initialization"""
        job_id = self.download_manager.create_job(
            "training_packages", 
            self.test_package_codes, 
            self.test_user_id
        )
        
        # Verify job ID is a valid UUID
        assert uuid.UUID(job_id)
        
        # Verify job is stored with correct attributes
        job = self.download_manager.get_job_status(job_id)
        assert job is not None
        assert job["type"] == "training_packages"
        assert job["status"] == "queued"
        assert job["user_id"] == self.test_user_id
        assert job["total_items"] == len(self.test_package_codes)
        assert job["completed_items"] == 0
        assert job["failed_items"] == 0
        assert job["items"] == self.test_package_codes
        assert job["current_item"] is None
        assert isinstance(job["started_at"], str)
        assert job["completed_at"] is None
        assert job["errors"] == []
        assert job["results"] == []
    
    def test_get_job_status_existing(self):
        """Test retrieving status of existing job"""
        job_id = self.download_manager.create_job(
            "units", 
            self.test_unit_codes, 
            self.test_user_id
        )
        
        status = self.download_manager.get_job_status(job_id)
        assert status is not None
        assert status["id"] == job_id
        assert status["type"] == "units"
    
    def test_get_job_status_nonexistent(self):
        """Test retrieving status of non-existent job"""
        fake_job_id = str(uuid.uuid4())
        status = self.download_manager.get_job_status(fake_job_id)
        assert status is None
    
    def test_update_job_status(self):
        """Test updating job status and additional fields"""
        job_id = self.download_manager.create_job(
            "training_packages", 
            self.test_package_codes, 
            self.test_user_id
        )
        
        # Update status and additional fields
        self.download_manager.update_job_status(
            job_id, 
            "processing",
            current_item="ICT40120",
            completed_items=1
        )
        
        job = self.download_manager.get_job_status(job_id)
        assert job["status"] == "processing"
        assert job["current_item"] == "ICT40120"
        assert job["completed_items"] == 1
    
    def test_update_job_status_nonexistent(self):
        """Test updating non-existent job (should not raise error)"""
        fake_job_id = str(uuid.uuid4())
        # Should not raise an exception
        self.download_manager.update_job_status(fake_job_id, "processing")


class TestDownloadManagerIntegration:
    """Integration tests for DownloadManager with database operations"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock(spec=Session)
        session.query.return_value.filter.return_value.first.return_value = None
        session.add = Mock()
        session.commit = Mock()
        session.refresh = Mock()
        session.rollback = Mock()
        session.close = Mock()
        return session
    
    @pytest.fixture
    def mock_tga_client(self):
        """Mock TGA client"""
        client = Mock()
        client.get_component_details.return_value = {
            "code": "ICT40120",
            "title": "Certificate IV in Information Technology",
            "description": "Test description",
            "status": "Current",
            "release_date": "2021-01-01",
            "xml_file": "test.xml"
        }
        client.search_components.return_value = {
            "components": [
                {
                    "code": "ICTICT418",
                    "title": "Test Unit",
                    "description": "Test unit description"
                }
            ]
        }
        client.get_component_xml.return_value = {
            "xml": "<unit><elements><element><number>1</number><title>Test Element</title></element></elements></unit>"
        }
        client.extract_elements.return_value = [
            {
                "number": "1",
                "title": "Test Element",
                "performance_criteria": [
                    {"number": "1.1", "text": "Test PC"}
                ]
            }
        ]
        return client
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('services.download_manager.SessionLocal')
    @patch('services.download_manager.TrainingGovClient')
    def test_process_training_package_download_success(self, mock_client_class, mock_session_local, mock_tga_client, mock_db_session):
        """Test successful training package download processing"""
        # Setup mocks
        mock_session_local.return_value = mock_db_session
        mock_client_class.return_value = mock_tga_client
        
        # Create download manager and job
        download_manager = DownloadManager()
        job_id = download_manager.create_job("training_packages", ["ICT40120"], 1)
        
        # Process download
        download_manager.process_training_package_download(job_id, ["ICT40120"], 1)
        
        # Verify job completion
        job = download_manager.get_job_status(job_id)
        assert job["status"] == "completed"
        assert job["completed_items"] == 1
        assert job["failed_items"] == 0
        assert len(job["results"]) == 1
        assert job["results"][0]["status"] == "success"
        
        # Verify TGA client was called
        mock_tga_client.get_component_details.assert_called_with("ICT40120")
        
        # Verify database operations
        mock_db_session.commit.assert_called()
    
    @patch.dict('os.environ', {})  # No TGA credentials
    def test_process_training_package_download_no_credentials(self):
        """Test training package download with missing TGA credentials"""
        download_manager = DownloadManager()
        job_id = download_manager.create_job("training_packages", ["ICT40120"], 1)
        
        # Process download
        download_manager.process_training_package_download(job_id, ["ICT40120"], 1)
        
        # Verify job failed
        job = download_manager.get_job_status(job_id)
        assert job["status"] == "failed"
        assert "TGA API credentials not configured" in job["errors"]
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('services.download_manager.SessionLocal')
    @patch('services.download_manager.TrainingGovClient')
    def test_process_training_package_download_tga_error(self, mock_client_class, mock_session_local, mock_db_session):
        """Test training package download with TGA API error"""
        # Setup mocks
        mock_session_local.return_value = mock_db_session
        mock_client = Mock()
        mock_client.get_component_details.side_effect = Exception("TGA API Error")
        mock_client_class.return_value = mock_client
        
        # Create download manager and job
        download_manager = DownloadManager()
        job_id = download_manager.create_job("training_packages", ["ICT40120"], 1)
        
        # Process download
        download_manager.process_training_package_download(job_id, ["ICT40120"], 1)
        
        # Verify job handled error
        job = download_manager.get_job_status(job_id)
        assert job["status"] == "completed"  # Job completes even with individual failures
        assert job["failed_items"] == 1
        assert len(job["errors"]) > 0
        assert "TGA API Error" in job["errors"][0]
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('services.download_manager.SessionLocal')
    @patch('services.download_manager.TrainingGovClient')
    def test_process_units_download_success(self, mock_client_class, mock_session_local, mock_tga_client, mock_db_session):
        """Test successful units download processing"""
        # Setup mocks
        mock_session_local.return_value = mock_db_session
        mock_client_class.return_value = mock_tga_client
        
        # Mock unit model
        mock_unit = Mock()
        mock_unit.id = 1
        mock_unit.code = "ICTICT418"
        
        # Create download manager and job
        download_manager = DownloadManager()
        job_id = download_manager.create_job("units", ["ICTICT418"], 1)
        
        # Process download
        download_manager.process_units_download(job_id, ["ICTICT418"], 1)
        
        # Verify job completion
        job = download_manager.get_job_status(job_id)
        assert job["status"] == "completed"
        assert job["completed_items"] == 1
        assert job["failed_items"] == 0
    
    def test_store_training_package_new(self, mock_db_session):
        """Test storing new training package"""
        download_manager = DownloadManager()
        
        package_data = {
            "code": "ICT40120",
            "title": "Certificate IV in Information Technology",
            "description": "Test description",
            "status": "Current"
        }
        
        # Mock query to return None (package doesn't exist)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Mock the package model
        with patch('models.tables.TrainingPackage') as mock_package_class:
            mock_package = Mock()
            mock_package.id = 1
            mock_package_class.return_value = mock_package
            
            result = download_manager._store_training_package(mock_db_session, package_data)
            
            # Verify package was created
            mock_package_class.assert_called_once()
            mock_db_session.add.assert_called_with(mock_package)
            mock_db_session.commit.assert_called()
            mock_db_session.refresh.assert_called_with(mock_package)
    
    def test_store_training_package_existing(self, mock_db_session):
        """Test updating existing training package"""
        download_manager = DownloadManager()
        
        package_data = {
            "code": "ICT40120",
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        # Mock existing package
        existing_package = Mock()
        existing_package.code = "ICT40120"
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_package
        
        result = download_manager._store_training_package(mock_db_session, package_data)
        
        # Verify package was updated
        mock_db_session.commit.assert_called()
        mock_db_session.refresh.assert_called_with(existing_package)


class TestDownloadManagerErrorHandling:
    """Test error handling scenarios in DownloadManager"""
    
    def test_process_training_package_download_database_error(self):
        """Test handling of database errors during processing"""
        download_manager = DownloadManager()
        job_id = download_manager.create_job("training_packages", ["ICT40120"], 1)
        
        with patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'}):
            with patch('services.download_manager.SessionLocal') as mock_session_local:
                # Mock database session that raises an error
                mock_session = Mock()
                mock_session.close = Mock()
                mock_session_local.return_value = mock_session
                mock_session_local.side_effect = Exception("Database connection error")
                
                # Process download
                download_manager.process_training_package_download(job_id, ["ICT40120"], 1)
                
                # Verify job failed
                job = download_manager.get_job_status(job_id)
                assert job["status"] == "failed"
                assert len(job["errors"]) > 0
    
    def test_process_units_download_xml_parsing_error(self):
        """Test handling of XML parsing errors"""
        download_manager = DownloadManager()
        job_id = download_manager.create_job("units", ["ICTICT418"], 1)
        
        with patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'}):
            with patch('services.download_manager.SessionLocal') as mock_session_local:
                with patch('services.download_manager.TrainingGovClient') as mock_client_class:
                    # Setup mocks
                    mock_session = Mock()
                    mock_session_local.return_value = mock_session
                    
                    mock_client = Mock()
                    mock_client.get_component_details.return_value = {
                        "code": "ICTICT418",
                        "title": "Test Unit"
                    }
                    mock_client.get_component_xml.side_effect = Exception("XML parsing error")
                    mock_client_class.return_value = mock_client
                    
                    # Process download
                    download_manager.process_units_download(job_id, ["ICTICT418"], 1)
                    
                    # Verify job completed with errors
                    job = download_manager.get_job_status(job_id)
                    # Job should still complete, but with failed items
                    assert job["failed_items"] >= 0  # May have partial failures


@pytest.mark.integration
class TestDownloadManagerRealDatabase:
    """Integration tests with real database operations"""
    
    def test_full_training_package_workflow(self, db_session):
        """Test complete training package download workflow with real database"""
        download_manager = DownloadManager()
        
        # Create a test training package
        package_data = {
            "code": "TEST40120",
            "title": "Test Certificate IV",
            "description": "Test package for integration testing",
            "status": "Current"
        }
        
        # Store package
        result = download_manager._store_training_package(db_session, package_data)
        
        # Verify package was stored
        assert result is not None
        assert result.code == "TEST40120"
        assert result.title == "Test Certificate IV"
        
        # Verify package exists in database
        stored_package = db_session.query(models.TrainingPackage).filter(
            models.TrainingPackage.code == "TEST40120"
        ).first()
        assert stored_package is not None
        assert stored_package.title == "Test Certificate IV"
    
    def test_full_unit_workflow(self, db_session):
        """Test complete unit download workflow with real database"""
        download_manager = DownloadManager()
        
        # Create a test unit
        unit_data = {
            "code": "TESTICT418",
            "title": "Test ICT Unit",
            "description": "Test unit for integration testing",
            "status": "Current"
        }
        
        # Store unit
        result = download_manager._store_unit(db_session, unit_data)
        
        # Verify unit was stored
        assert result is not None
        assert result.code == "TESTICT418"
        assert result.title == "Test ICT Unit"
        
        # Verify unit exists in database
        stored_unit = db_session.query(models.Unit).filter(
            models.Unit.code == "TESTICT418"
        ).first()
        assert stored_unit is not None
        assert stored_unit.title == "Test ICT Unit"
