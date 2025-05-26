"""
Tests for Training Packages Bulk Download API

This module tests the enhanced training packages router with bulk download
functionality, including admin endpoints and progress tracking.
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from main import app
import models.tables as models
from services.download_manager import download_manager


class TestAvailableTrainingPackages:
    """Test the /available endpoint for discovering training packages"""
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.training_packages.TrainingGovClient')
    def test_get_available_training_packages_success(self, mock_client_class, test_client, authenticated_admin, test_db_session):
        """Test successful retrieval of available training packages"""
        admin_user, admin_token = authenticated_admin
        
        # Mock TGA client response
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "ICT40120",
                    "title": "Certificate IV in Information Technology",
                    "description": "Test description",
                    "status": "Current"
                },
                {
                    "code": "BSB50420",
                    "title": "Diploma of Leadership and Management",
                    "description": "Test description 2",
                    "status": "Current"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        # Make request
        response = test_client.get(
            "/api/training-packages/available",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "packages" in data
        assert len(data["packages"]) == 2
        assert data["packages"][0]["code"] == "ICT40120"
        assert data["packages"][1]["code"] == "BSB50420"
        assert data["page"] == 1
        assert data["page_size"] == 50
    
    def test_get_available_training_packages_unauthorized(self, test_client):
        """Test access without authentication"""
        response = test_client.get("/api/training-packages/available")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_available_training_packages_non_admin(self, test_client, authenticated_user_token):
        """Test access with non-admin user"""
        response = test_client.get(
            "/api/training-packages/available",
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch.dict('os.environ', {})  # No TGA credentials
    def test_get_available_training_packages_no_credentials(self, test_client, authenticated_admin):
        """Test with missing TGA credentials"""
        admin_user, admin_token = authenticated_admin
        response = test_client.get(
            "/api/training-packages/available",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "TGA API credentials not configured" in response.json()["detail"]
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.training_packages.TrainingGovClient')
    def test_get_available_training_packages_tga_error(self, mock_client_class, test_client, authenticated_admin):
        """Test TGA API error handling"""
        admin_user, admin_token = authenticated_admin
        
        # Mock TGA client to raise exception
        mock_client = Mock()
        mock_client.search_components.side_effect = Exception("TGA API Error")
        mock_client_class.return_value = mock_client
        
        response = test_client.get(
            "/api/training-packages/available",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve available training packages" in response.json()["detail"]


class TestBulkDownloadTrainingPackages:
    """Test the bulk download endpoint for training packages"""
    
    @patch('routers.training_packages.download_manager')
    def test_bulk_download_training_packages_success(self, mock_download_manager, test_client, authenticated_admin):
        """Test successful bulk download initiation"""
        admin_user, admin_token = authenticated_admin
        
        # Mock download manager
        test_job_id = str(uuid.uuid4())
        mock_download_manager.create_job.return_value = test_job_id
        
        # Request data
        package_codes = ["ICT40120", "BSB50420"]
        
        # Make request
        response = test_client.post(
            "/api/training-packages/bulk-download",
            json=package_codes,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == test_job_id
        assert "Bulk download started for 2 training packages" in data["message"]
        assert data["status"] == "queued"
        
        # Verify download manager was called
        mock_download_manager.create_job.assert_called_once_with(
            "training_packages", package_codes, int(admin_user.id)
        )
    
    def test_bulk_download_training_packages_unauthorized(self, test_client):
        """Test bulk download without authentication"""
        response = test_client.post(
            "/api/training-packages/bulk-download",
            json=["ICT40120"]
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_bulk_download_training_packages_non_admin(self, test_client, authenticated_user_token):
        """Test bulk download with non-admin user"""
        response = test_client.post(
            "/api/training-packages/bulk-download",
            json=["ICT40120"],
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_bulk_download_training_packages_empty_list(self, test_client, authenticated_admin):
        """Test bulk download with empty package list"""
        admin_user, admin_token = authenticated_admin
        response = test_client.post(
            "/api/training-packages/bulk-download",
            json=[],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No training package codes provided" in response.json()["detail"]
    
    @patch('routers.training_packages.download_manager')
    def test_bulk_download_training_packages_large_list(self, mock_download_manager, test_client, authenticated_admin):
        """Test bulk download with large package list"""
        admin_user, admin_token = authenticated_admin
        
        # Mock download manager
        test_job_id = str(uuid.uuid4())
        mock_download_manager.create_job.return_value = test_job_id
        
        # Large list of package codes
        package_codes = [f"TEST{i:05d}" for i in range(100)]
        
        response = test_client.post(
            "/api/training-packages/bulk-download",
            json=package_codes,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Bulk download started for 100 training packages" in data["message"]


class TestDownloadStatus:
    """Test the download status endpoint"""
    
    @patch('routers.training_packages.download_manager')
    def test_get_download_status_success(self, mock_download_manager, test_client, authenticated_admin):
        """Test successful download status retrieval"""
        admin_user, admin_token = authenticated_admin
        
        # Mock download manager response
        test_job_id = str(uuid.uuid4())
        mock_status = {
            "id": test_job_id,
            "type": "training_packages",
            "status": "processing",
            "total_items": 2,
            "completed_items": 1,
            "failed_items": 0,
            "current_item": "BSB50420",
            "errors": []
        }
        mock_download_manager.get_job_status.return_value = mock_status
        
        # Make request
        response = test_client.get(
            f"/api/training-packages/download-status/{test_job_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_job_id
        assert data["status"] == "processing"
        assert data["completed_items"] == 1
        assert data["current_item"] == "BSB50420"
    
    @patch('routers.training_packages.download_manager')
    def test_get_download_status_not_found(self, mock_download_manager, test_client, authenticated_admin):
        """Test download status for non-existent job"""
        admin_user, admin_token = authenticated_admin
        
        # Mock download manager to return None
        mock_download_manager.get_job_status.return_value = None
        
        test_job_id = str(uuid.uuid4())
        response = test_client.get(
            f"/api/training-packages/download-status/{test_job_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Download job not found" in response.json()["detail"]
    
    def test_get_download_status_unauthorized(self, test_client):
        """Test download status without authentication"""
        test_job_id = str(uuid.uuid4())
        response = test_client.get(f"/api/training-packages/download-status/{test_job_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_download_status_non_admin(self, test_client, authenticated_user_token):
        """Test download status with non-admin user"""
        test_job_id = str(uuid.uuid4())
        response = test_client.get(
            f"/api/training-packages/download-status/{test_job_id}",
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestTrainingPackagesSearch:
    """Test enhanced search functionality"""
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.training_packages.TrainingGovClient')
    def test_search_training_packages_with_tga_fallback(self, mock_client_class, test_client, test_db_session):
        """Test search that falls back to TGA when local results are insufficient"""
        # Create minimal local data
        local_package = models.TrainingPackage(
            code="LOCAL001",
            title="Local Package",
            description="Local test package",
            visible=True
        )
        test_db_session.add(local_package)
        test_db_session.commit()
        
        # Mock TGA client response
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "TGA001",
                    "title": "TGA Package",
                    "description": "TGA test package",
                    "status": "Current"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        # Make search request
        response = test_client.post(
            "/api/training-packages/search",
            json={
                "query": "test",
                "page": 1,
                "page_size": 20
            }
        )
        
        # Verify response includes both local and TGA results
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1  # Should have at least the TGA result
        
        # Verify TGA client was called
        mock_client.search_components.assert_called_once()


@pytest.mark.integration
class TestTrainingPackagesBulkIntegration:
    """Integration tests for training packages bulk functionality"""
    
    def test_full_bulk_download_workflow(self, test_client, authenticated_admin, test_db_session):
        """Test complete bulk download workflow with real database"""
        admin_user, admin_token = authenticated_admin
        
        # Clear any existing download manager jobs
        download_manager.jobs.clear()
        
        # Step 1: Initiate bulk download
        package_codes = ["TEST001", "TEST002"]
        
        with patch('routers.training_packages.download_manager.process_training_package_download'):
            response = test_client.post(
                "/api/training-packages/bulk-download",
                json=package_codes,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            job_id = response.json()["job_id"]
        
        # Step 2: Check job status
        response = test_client.get(
            f"/api/training-packages/download-status/{job_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        status_data = response.json()
        assert status_data["id"] == job_id
        assert status_data["type"] == "training_packages"
        assert status_data["status"] == "queued"
        assert status_data["total_items"] == 2
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.training_packages.TrainingGovClient')
    def test_available_packages_with_database_check(self, mock_client_class, test_client, authenticated_admin, test_db_session):
        """Test available packages endpoint with database status checking"""
        admin_user, admin_token = authenticated_admin
        
        # Create existing package in database
        existing_package = models.TrainingPackage(
            code="ICT40120",
            title="Existing Package",
            processed="Y",
            visible=True
        )
        test_db_session.add(existing_package)
        test_db_session.commit()
        
        # Mock TGA response
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "ICT40120",
                    "title": "Certificate IV in Information Technology",
                    "description": "Existing package",
                    "status": "Current"
                },
                {
                    "code": "BSB50420",
                    "title": "Diploma of Leadership and Management",
                    "description": "New package",
                    "status": "Current"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        # Make request
        response = test_client.get(
            "/api/training-packages/available",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        packages = data["packages"]
        
        # Find the existing package
        existing_pkg = next(p for p in packages if p["code"] == "ICT40120")
        new_pkg = next(p for p in packages if p["code"] == "BSB50420")
        
        # Verify database status is correctly indicated
        assert existing_pkg["in_database"] is True
        assert existing_pkg["processed"] == "Y"
        assert new_pkg["in_database"] is False
        assert new_pkg["processed"] == "N"


class TestTrainingPackagesErrorHandling:
    """Test error handling in training packages bulk functionality"""
    
    @patch('routers.training_packages.download_manager')
    def test_bulk_download_with_download_manager_error(self, mock_download_manager, test_client, authenticated_admin):
        """Test bulk download when download manager raises an error"""
        admin_user, admin_token = authenticated_admin
        
        # Mock download manager to raise exception
        mock_download_manager.create_job.side_effect = Exception("Download manager error")
        
        response = test_client.post(
            "/api/training-packages/bulk-download",
            json=["ICT40120"],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should return 500 error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_invalid_job_id_format(self, test_client, authenticated_admin):
        """Test download status with invalid job ID format"""
        admin_user, admin_token = authenticated_admin
        
        response = test_client.get(
            "/api/training-packages/download-status/invalid-job-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should handle gracefully (download manager will return None)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.training_packages.TrainingGovClient')
    def test_available_packages_partial_tga_failure(self, mock_client_class, test_client, authenticated_admin):
        """Test available packages when TGA returns partial data"""
        admin_user, admin_token = authenticated_admin
        
        # Mock TGA client to return malformed data
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "ICT40120",
                    "title": "Valid Package"
                    # Missing other fields
                },
                {
                    # Missing code field
                    "title": "Invalid Package"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        response = test_client.get(
            "/api/training-packages/available",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should still return 200 but handle malformed data gracefully
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "packages" in data
