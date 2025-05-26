"""
Tests for Units Bulk Download API

This module tests the enhanced units router with bulk download functionality,
comprehensive data retrieval, and admin endpoints.
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from main import app
import models.tables as models
from services.download_manager import download_manager


class TestUnitsBulkAPI:
    """Test cases for units bulk download API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    @pytest.fixture
    def admin_user(self, db_session):
        """Create admin user for testing"""
        # Create admin role
        admin_role = models.Role(name="admin", description="Administrator")
        db_session.add(admin_role)
        db_session.commit()
        
        # Create admin user
        admin_user = models.User(
            username="admin_test",
            email="admin@test.com",
            hashed_password="hashed_password",
            role_id=admin_role.id
        )
        db_session.add(admin_user)
        db_session.commit()
        return admin_user
    
    @pytest.fixture
    def regular_user(self, db_session):
        """Create regular user for testing"""
        # Create user role
        user_role = models.Role(name="user", description="Regular User")
        db_session.add(user_role)
        db_session.commit()
        
        # Create regular user
        regular_user = models.User(
            username="user_test",
            email="user@test.com",
            hashed_password="hashed_password",
            role_id=user_role.id
        )
        db_session.add(regular_user)
        db_session.commit()
        return regular_user
    
    @pytest.fixture
    def admin_token(self, admin_user):
        """Generate JWT token for admin user"""
        from auth.auth_handler import signJWT
        return signJWT(admin_user.id)["access_token"]
    
    @pytest.fixture
    def user_token(self, regular_user):
        """Generate JWT token for regular user"""
        from auth.auth_handler import signJWT
        return signJWT(regular_user.id)["access_token"]
    
    @pytest.fixture
    def sample_unit(self, db_session):
        """Create sample unit with elements and performance criteria"""
        unit = models.Unit(
            code="TESTICT418",
            title="Test ICT Unit",
            description="Test unit for comprehensive testing",
            status="Current",
            visible=True
        )
        db_session.add(unit)
        db_session.commit()
        
        # Add elements
        element1 = models.UnitElement(
            unit_id=unit.id,
            element_num="1",
            element_text="Test Element 1"
        )
        element2 = models.UnitElement(
            unit_id=unit.id,
            element_num="2", 
            element_text="Test Element 2"
        )
        db_session.add_all([element1, element2])
        db_session.commit()
        
        # Add performance criteria
        pc1 = models.UnitPerformanceCriteria(
            unit_id=unit.id,
            element_id=element1.id,
            pc_num="1.1",
            pc_text="Test Performance Criteria 1.1"
        )
        pc2 = models.UnitPerformanceCriteria(
            unit_id=unit.id,
            element_id=element1.id,
            pc_num="1.2",
            pc_text="Test Performance Criteria 1.2"
        )
        pc3 = models.UnitPerformanceCriteria(
            unit_id=unit.id,
            element_id=element2.id,
            pc_num="2.1",
            pc_text="Test Performance Criteria 2.1"
        )
        db_session.add_all([pc1, pc2, pc3])
        db_session.commit()
        
        return unit


class TestAvailableUnits:
    """Test the /available endpoint for discovering units"""
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.units.TrainingGovClient')
    def test_get_available_units_success(self, mock_client_class, client, admin_token, db_session):
        """Test successful retrieval of available units"""
        # Mock TGA client response
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "ICTICT418",
                    "title": "Contribute to copyright, ethics and privacy in an ICT environment",
                    "description": "Test description",
                    "status": "Current"
                },
                {
                    "code": "BSBWHS411",
                    "title": "Implement and monitor WHS policies, procedures and programs",
                    "description": "Test description 2",
                    "status": "Current"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        # Make request
        response = client.get(
            "/api/units/available",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "units" in data
        assert len(data["units"]) == 2
        assert data["units"][0]["code"] == "ICTICT418"
        assert data["units"][1]["code"] == "BSBWHS411"
        assert data["page"] == 1
        assert data["page_size"] == 50
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.units.TrainingGovClient')
    def test_get_available_units_with_training_package_filter(self, mock_client_class, client, admin_token):
        """Test available units with training package filter"""
        # Mock TGA client response
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "ICTICT418",
                    "title": "ICT Unit",
                    "description": "ICT test unit",
                    "status": "Current"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        # Make request with training package filter
        response = client.get(
            "/api/units/available?training_package_code=ICT40120",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["filter"] == "ICT40120"
        
        # Verify TGA client was called with filter
        mock_client.search_components.assert_called_once()
        call_args = mock_client.search_components.call_args
        assert call_args[1]["filter_text"] == "ICT40120"
    
    def test_get_available_units_unauthorized(self, client):
        """Test access without authentication"""
        response = client.get("/api/units/available")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_available_units_non_admin(self, client, user_token):
        """Test access with non-admin user"""
        response = client.get(
            "/api/units/available",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestBulkDownloadUnits:
    """Test the bulk download endpoint for units"""
    
    @patch('routers.units.download_manager')
    def test_bulk_download_units_success(self, mock_download_manager, client, admin_token):
        """Test successful bulk download initiation"""
        # Mock download manager
        test_job_id = str(uuid.uuid4())
        mock_download_manager.create_job.return_value = test_job_id
        
        # Request data
        unit_codes = ["ICTICT418", "BSBWHS411"]
        
        # Make request
        response = client.post(
            "/api/units/bulk-download",
            json=unit_codes,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == test_job_id
        assert "Bulk download started for 2 units" in data["message"]
        assert data["status"] == "queued"
        
        # Verify download manager was called
        mock_download_manager.create_job.assert_called_once_with(
            "units", unit_codes, 1  # admin_user.id
        )
    
    def test_bulk_download_units_unauthorized(self, client):
        """Test bulk download without authentication"""
        response = client.post(
            "/api/units/bulk-download",
            json=["ICTICT418"]
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_bulk_download_units_non_admin(self, client, user_token):
        """Test bulk download with non-admin user"""
        response = client.post(
            "/api/units/bulk-download",
            json=["ICTICT418"],
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_bulk_download_units_empty_list(self, client, admin_token):
        """Test bulk download with empty unit list"""
        response = client.post(
            "/api/units/bulk-download",
            json=[],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No unit codes provided" in response.json()["detail"]


class TestUnitElements:
    """Test unit elements endpoint"""
    
    def test_get_unit_elements_success(self, client, sample_unit, db_session):
        """Test successful retrieval of unit elements"""
        response = client.get(f"/api/units/{sample_unit.id}/elements")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["unit_code"] == "TESTICT418"
        assert data["unit_title"] == "Test ICT Unit"
        assert len(data["elements"]) == 2
        assert data["elements"][0]["element_num"] == "1"
        assert data["elements"][0]["element_text"] == "Test Element 1"
        assert data["elements"][1]["element_num"] == "2"
        assert data["elements"][1]["element_text"] == "Test Element 2"
    
    def test_get_unit_elements_not_found(self, client):
        """Test elements for non-existent unit"""
        response = client.get("/api/units/99999/elements")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Unit not found" in response.json()["detail"]


class TestUnitPerformanceCriteria:
    """Test unit performance criteria endpoint"""
    
    def test_get_unit_performance_criteria_success(self, client, sample_unit, db_session):
        """Test successful retrieval of unit performance criteria"""
        response = client.get(f"/api/units/{sample_unit.id}/performance-criteria")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["unit_code"] == "TESTICT418"
        assert data["unit_title"] == "Test ICT Unit"
        assert len(data["performance_criteria"]) == 3
        
        # Verify performance criteria are ordered by element and PC number
        pc_data = data["performance_criteria"]
        assert pc_data[0]["element_num"] == "1"
        assert pc_data[0]["pc_num"] == "1.1"
        assert pc_data[1]["element_num"] == "1"
        assert pc_data[1]["pc_num"] == "1.2"
        assert pc_data[2]["element_num"] == "2"
        assert pc_data[2]["pc_num"] == "2.1"
    
    def test_get_unit_performance_criteria_not_found(self, client):
        """Test performance criteria for non-existent unit"""
        response = client.get("/api/units/99999/performance-criteria")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Unit not found" in response.json()["detail"]


class TestUnitComprehensive:
    """Test comprehensive unit data endpoint"""
    
    def test_get_unit_comprehensive_success(self, client, sample_unit, db_session):
        """Test successful retrieval of comprehensive unit data"""
        response = client.get(f"/api/units/{sample_unit.id}/comprehensive")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify unit data
        unit_data = data["unit"]
        assert unit_data["code"] == "TESTICT418"
        assert unit_data["title"] == "Test ICT Unit"
        assert unit_data["description"] == "Test unit for comprehensive testing"
        
        # Verify elements with performance criteria
        elements = data["elements"]
        assert len(elements) == 2
        
        element1 = elements[0]
        assert element1["element_num"] == "1"
        assert element1["element_text"] == "Test Element 1"
        assert len(element1["performance_criteria"]) == 2
        assert element1["performance_criteria"][0]["pc_num"] == "1.1"
        assert element1["performance_criteria"][1]["pc_num"] == "1.2"
        
        element2 = elements[1]
        assert element2["element_num"] == "2"
        assert element2["element_text"] == "Test Element 2"
        assert len(element2["performance_criteria"]) == 1
        assert element2["performance_criteria"][0]["pc_num"] == "2.1"
        
        # Verify critical aspects and required skills (empty for now)
        assert data["critical_aspects"] == []
        assert data["required_skills"] == []
    
    def test_get_unit_comprehensive_not_found(self, client):
        """Test comprehensive data for non-existent unit"""
        response = client.get("/api/units/99999/comprehensive")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Unit not found" in response.json()["detail"]


class TestUnitsSearch:
    """Test enhanced search functionality for units"""
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.units.TrainingGovClient')
    def test_search_units_with_tga_fallback(self, mock_client_class, client, db_session):
        """Test search that falls back to TGA when local results are insufficient"""
        # Create minimal local data
        local_unit = models.Unit(
            code="LOCAL001",
            title="Local Unit",
            description="Local test unit",
            visible=True
        )
        db_session.add(local_unit)
        db_session.commit()
        
        # Mock TGA client response
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "TGA001",
                    "title": "TGA Unit",
                    "description": "TGA test unit",
                    "status": "Current"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        # Make search request
        response = client.post(
            "/api/units/search",
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
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.units.TrainingGovClient')
    def test_search_units_with_training_package_filter(self, mock_client_class, client, db_session):
        """Test search with training package filter"""
        # Mock TGA client response
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "ICTICT418",
                    "title": "ICT Unit",
                    "description": "ICT test unit",
                    "status": "Current"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        # Make search request with training package filter
        response = client.post(
            "/api/units/search",
            json={
                "query": "test",
                "training_package_code": "ICT40120",
                "page": 1,
                "page_size": 20
            }
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        # Verify TGA client was called with combined filter
        mock_client.search_components.assert_called_once()
        call_args = mock_client.search_components.call_args
        assert "ICT40120 test" in call_args[1]["filter_text"]


class TestUnitVisibility:
    """Test unit visibility management"""
    
    def test_set_unit_visibility_success(self, client, admin_token, sample_unit, db_session):
        """Test successful unit visibility update"""
        response = client.put(
            f"/api/units/{sample_unit.id}/visibility",
            json=False,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert f"Unit {sample_unit.code} visibility set to False" in data["message"]
        
        # Verify unit visibility was updated in database
        db_session.refresh(sample_unit)
        assert sample_unit.visible is False
    
    def test_set_unit_visibility_unauthorized(self, client, sample_unit):
        """Test visibility update without authentication"""
        response = client.put(
            f"/api/units/{sample_unit.id}/visibility",
            json=False
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_set_unit_visibility_non_admin(self, client, user_token, sample_unit):
        """Test visibility update with non-admin user"""
        response = client.put(
            f"/api/units/{sample_unit.id}/visibility",
            json=False,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_set_unit_visibility_not_found(self, client, admin_token):
        """Test visibility update for non-existent unit"""
        response = client.put(
            "/api/units/99999/visibility",
            json=False,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Unit not found" in response.json()["detail"]


@pytest.mark.integration
class TestUnitsBulkIntegration:
    """Integration tests for units bulk functionality"""
    
    def test_full_bulk_download_workflow(self, client, admin_token, db_session):
        """Test complete bulk download workflow with real database"""
        # Clear any existing download manager jobs
        download_manager.jobs.clear()
        
        # Step 1: Initiate bulk download
        unit_codes = ["TESTICT001", "TESTICT002"]
        
        with patch('routers.units.download_manager.process_units_download'):
            response = client.post(
                "/api/units/bulk-download",
                json=unit_codes,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            job_id = response.json()["job_id"]
        
        # Step 2: Check job status
        response = client.get(
            f"/api/units/download-status/{job_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        status_data = response.json()
        assert status_data["id"] == job_id
        assert status_data["type"] == "units"
        assert status_data["status"] == "queued"
        assert status_data["total_items"] == 2
    
    def test_comprehensive_unit_data_workflow(self, client, db_session):
        """Test complete unit data retrieval workflow"""
        # Create unit with comprehensive data
        unit = models.Unit(
            code="COMPREHENSIVE001",
            title="Comprehensive Test Unit",
            description="Unit for testing comprehensive data retrieval",
            status="Current",
            visible=True
        )
        db_session.add(unit)
        db_session.commit()
        
        # Add elements
        element = models.UnitElement(
            unit_id=unit.id,
            element_num="1",
            element_text="Comprehensive Element"
        )
        db_session.add(element)
        db_session.commit()
        
        # Add performance criteria
        pc = models.UnitPerformanceCriteria(
            unit_id=unit.id,
            element_id=element.id,
            pc_num="1.1",
            pc_text="Comprehensive Performance Criteria"
        )
        db_session.add(pc)
        db_session.commit()
        
        # Test comprehensive endpoint
        response = client.get(f"/api/units/{unit.id}/comprehensive")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["unit"]["code"] == "COMPREHENSIVE001"
        assert len(data["elements"]) == 1
        assert len(data["elements"][0]["performance_criteria"]) == 1
        assert data["elements"][0]["performance_criteria"][0]["pc_text"] == "Comprehensive Performance Criteria"


class TestUnitsErrorHandling:
    """Test error handling in units bulk functionality"""
    
    @patch('routers.units.download_manager')
    def test_bulk_download_with_download_manager_error(self, mock_download_manager, client, admin_token):
        """Test bulk download when download manager raises an error"""
        # Mock download manager to raise exception
        mock_download_manager.create_job.side_effect = Exception("Download manager error")
        
        response = client.post(
            "/api/units/bulk-download",
            json=["ICTICT418"],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should return 500 error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @patch.dict('os.environ', {'TGA_USERNAME': 'test', 'TGA_PASSWORD': 'test'})
    @patch('routers.units.TrainingGovClient')
    def test_available_units_partial_tga_failure(self, mock_client_class, client, admin_token):
        """Test available units when TGA returns partial data"""
        # Mock TGA client to return malformed data
        mock_client = Mock()
        mock_client.search_components.return_value = {
            "components": [
                {
                    "code": "ICTICT418",
                    "title": "Valid Unit"
                    # Missing other fields
                },
                {
                    # Missing code field
                    "title": "Invalid Unit"
                }
            ]
        }
        mock_client_class.return_value = mock_client
        
        response = client.get(
            "/api/units/available",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should still return 200 but handle malformed data gracefully
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "units" in data
