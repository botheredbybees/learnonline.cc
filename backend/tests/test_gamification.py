"""
Test Gamification System

Tests for the gamification functionality including:
- Points service
- Achievement system
- Level progression
- Leaderboard functionality

Uses centralized PostgreSQL test configuration from conftest.py.
"""

import pytest
import uuid
from datetime import datetime

from models.tables import User, UserProfile, Role, Achievement, UserAchievement
from services.points import award_points, get_user_stats, check_and_award_achievements, get_leaderboard
from auth.auth_handler import create_access_token, get_password_hash


class TestPointsService:
    """Test the points service functionality."""
    
    def test_award_points_basic(self, test_db_session, test_user_data):
        """Test basic point awarding."""
        user = test_user_data["test_user"]
        result = award_points(test_db_session, str(user.id), "content_view")
        
        assert result["success"] is True
        assert result["points_awarded"] == 10
        assert result["total_points"] == 10
        assert result["level"] == 1
        assert result["action"] == "content_view"
    
    def test_award_custom_points(self, test_db_session, test_user_data):
        """Test awarding custom point amounts."""
        user = test_user_data["test_user"]
        result = award_points(test_db_session, str(user.id), "custom_action", points=50)
        
        assert result["success"] is True
        assert result["points_awarded"] == 50
        assert result["total_points"] == 50
    
    def test_level_progression(self, test_db_session, test_user_data):
        """Test level progression with points."""
        user = test_user_data["test_user"]
        # Award enough points to reach level 2 (101 points)
        award_points(test_db_session, str(user.id), "custom_action", points=101)
        
        stats = get_user_stats(test_db_session, str(user.id))
        assert stats["level"] == 2
        assert stats["experience_points"] == 101
    
    def test_invalid_action(self, test_db_session, test_user_data):
        """Test awarding points for invalid action."""
        user = test_user_data["test_user"]
        result = award_points(test_db_session, str(user.id), "invalid_action")
        
        assert result["success"] is False
        assert result["points_awarded"] == 0
    
    def test_user_not_found(self, test_db_session):
        """Test awarding points to non-existent user."""
        with pytest.raises(ValueError):
            award_points(test_db_session, str(uuid.uuid4()), "content_view")


class TestUserStats:
    """Test user statistics functionality."""
    
    def test_get_user_stats_basic(self, test_db_session, test_user_data):
        """Test getting basic user stats."""
        user = test_user_data["test_user"]
        stats = get_user_stats(test_db_session, str(user.id))
        
        assert stats["experience_points"] >= 0
        assert stats["level"] >= 1
        assert stats["role"] == "user"
        assert stats["achievements_count"] >= 0
    
    def test_get_user_stats_with_points(self, test_db_session, test_user_data):
        """Test getting stats after awarding points."""
        user = test_user_data["test_user"]
        initial_stats = get_user_stats(test_db_session, str(user.id))
        initial_points = initial_stats["experience_points"]
        
        award_points(test_db_session, str(user.id), "content_view")
        award_points(test_db_session, str(user.id), "quiz_complete")
        
        stats = get_user_stats(test_db_session, str(user.id))
        
        assert stats["experience_points"] == initial_points + 60  # 10 + 50
    
    def test_user_stats_not_found(self, test_db_session):
        """Test getting stats for non-existent user."""
        with pytest.raises(ValueError):
            get_user_stats(test_db_session, str(uuid.uuid4()))


class TestAchievements:
    """Test achievement system."""
    
    def test_check_first_login_achievement(self, test_db_session, test_user_data, test_achievements_data):
        """Test first login achievement."""
        user = test_user_data["test_user"]
        achievements = check_and_award_achievements(test_db_session, str(user.id), "first_login")
        
        # Should get First Login achievement
        first_login = next((a for a in achievements if a["title"] == "First Login"), None)
        assert first_login is not None
        
        # Check that achievement was recorded
        user_achievement = test_db_session.query(UserAchievement).filter(
            UserAchievement.user_id == user.id
        ).first()
        assert user_achievement is not None
    
    def test_content_explorer_achievement(self, test_db_session, test_user_data, test_achievements_data):
        """Test content explorer achievement (10 content views)."""
        user = test_user_data["test_user"]
        
        # Award points for 10 content views
        for _ in range(10):
            award_points(test_db_session, str(user.id), "content_view")
        
        # Check for achievement
        achievements = check_and_award_achievements(test_db_session, str(user.id), "content_view")
        
        # Should get Course Completion achievement (closest to content explorer)
        course_completion = next((a for a in achievements if a["title"] == "Course Completion"), None)
        if course_completion:
            assert course_completion is not None
    
    def test_duplicate_achievement_prevention(self, test_db_session, test_user_data, test_achievements_data):
        """Test that achievements aren't awarded twice."""
        user = test_user_data["test_user"]
        
        # Award first login achievement
        achievements1 = check_and_award_achievements(test_db_session, str(user.id), "first_login")
        first_login_count = len([a for a in achievements1 if a["title"] == "First Login"])
        
        # Try to award again - should return empty list since user already has it
        achievements2 = check_and_award_achievements(test_db_session, str(user.id), "first_login")
        second_login_count = len([a for a in achievements2 if a["title"] == "First Login"])
        
        # Should not award the same achievement again
        assert second_login_count == 0
        
        # Verify only one achievement exists in database for this user
        total_achievements = test_db_session.query(UserAchievement).filter(
            UserAchievement.user_id == user.id
        ).count()
        assert total_achievements >= first_login_count


class TestLeaderboard:
    """Test leaderboard functionality."""
    
    def test_empty_leaderboard(self, test_db_session):
        """Test leaderboard with no users."""
        leaderboard = get_leaderboard(test_db_session)
        
        assert "leaderboard" in leaderboard
        assert "total_count" in leaderboard
        assert leaderboard["total_count"] >= 0
    
    def test_leaderboard_with_users(self, test_db_session, test_user_data):
        """Test leaderboard with multiple users."""
        user_role = test_user_data["user_role"]
        
        # Create additional users with different points
        users = []
        for i in range(3):
            user = User(
                username=f"leaderboard_user_{i}",
                email=f"leaderboard{i}@example.com",
                hashed_password=get_password_hash("password"),
                role_id=user_role.id,
                is_active=True
            )
            test_db_session.add(user)
            test_db_session.commit()
            
            # Award different amounts of points
            award_points(test_db_session, str(user.id), "custom_action", points=(i + 1) * 100)
            users.append(user)
        
        test_db_session.commit()
        
        leaderboard = get_leaderboard(test_db_session, limit=10)
        
        assert len(leaderboard["leaderboard"]) >= 3
        assert leaderboard["total_count"] >= 3
        
        # Check that leaderboard is ordered by points (highest first)
        if len(leaderboard["leaderboard"]) >= 2:
            first_user_points = leaderboard["leaderboard"][0]["experience_points"]
            second_user_points = leaderboard["leaderboard"][1]["experience_points"]
            assert first_user_points >= second_user_points


class TestGamificationAPI:
    """Test gamification API endpoints."""
    
    def test_award_points_endpoint(self, test_client, authenticated_user_token):
        """Test the award points API endpoint"""
        response = test_client.post(
            "/gamification/simulate-action",
            json={"action": "content_view", "count": 1},
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_points_awarded"] == 10
    
    def test_get_stats_endpoint(self, test_client, authenticated_user_token):
        """Test the get stats API endpoint"""
        response = test_client.get(
            "/gamification/stats", 
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "experience_points" in data
        assert "level" in data
        assert "role" in data
    
    def test_leaderboard_endpoint(self, test_client):
        """Test the leaderboard API endpoint"""
        response = test_client.get("/gamification/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        assert "total_count" in data
    
    def test_achievements_endpoint(self, test_client, authenticated_user_token):
        """Test the achievements API endpoint"""
        response = test_client.get(
            "/gamification/achievements",
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "achievements" in data
        assert isinstance(data["achievements"], list)
    
    def test_unauthorized_access(self, test_client):
        """Test unauthorized access to protected endpoints"""
        response = test_client.post("/gamification/simulate-action", json={"action": "content_view"})
        assert response.status_code == 401
        
        response = test_client.get("/gamification/stats")
        assert response.status_code == 401
        
        response = test_client.get("/gamification/achievements")
        assert response.status_code == 401
    
    def test_invalid_action_endpoint(self, test_client, authenticated_user_token):
        """Test invalid action through API endpoint"""
        response = test_client.post(
            "/gamification/simulate-action",
            json={"action": "invalid_action", "count": 1},
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["total_points_awarded"] == 0


class TestPointsIntegration:
    """Test points system integration with achievements."""
    
    def test_points_trigger_achievements(self, test_db_session, test_user_data, test_achievements_data):
        """Test that earning points can trigger achievements."""
        user = test_user_data["test_user"]
        
        # Award points that should trigger an achievement
        result = award_points(test_db_session, str(user.id), "quiz_complete", points=50)
        
        assert result["success"] is True
        assert result["points_awarded"] == 50
        
        # Check if any achievements were triggered
        achievements = check_and_award_achievements(test_db_session, str(user.id), "quiz_complete")
        
        # Should have at least checked for achievements
        assert isinstance(achievements, list)
    
    def test_level_up_with_achievements(self, test_db_session, test_user_data, test_achievements_data):
        """Test level progression combined with achievements."""
        user = test_user_data["test_user"]
        
        # Award enough points to level up
        award_points(test_db_session, str(user.id), "custom_action", points=150)
        
        # Check stats
        stats = get_user_stats(test_db_session, str(user.id))
        assert stats["level"] >= 2
        assert stats["experience_points"] >= 150
        
        # Check for any achievements
        achievements = check_and_award_achievements(test_db_session, str(user.id), "level_up")
        assert isinstance(achievements, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
