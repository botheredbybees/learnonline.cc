from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from typing import ForwardRef

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class RoleSchema(BaseSchema):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

class PermissionSchema(BaseSchema):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

class UserSchema(BaseSchema):
    id: UUID  # Use standard Python uuid.UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role_id: Optional[int] = None
    last_login: Optional[datetime] = None

class UserRegisterSchema(BaseSchema):
    """Schema for user registration"""
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLoginSchema(BaseSchema):
    """Schema for user login"""
    email: str
    password: str

class PasswordResetRequestSchema(BaseSchema):
    """Schema for password reset request"""
    email: str

class PasswordResetSchema(BaseSchema):
    """Schema for password reset"""
    token: str
    new_password: str

class UserUpdateSchema(BaseSchema):
    """Schema for user updates - excludes id and other fields that shouldn't be directly updated"""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None

class TrainingPackageSchema(BaseSchema):
    id: Optional[int] = None
    code: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    release_date: Optional[datetime] = None
    xml_file: Optional[str] = None
    processed: Optional[str] = 'N'
    visible: bool = True

class TrainingPackageCreateSchema(BaseSchema):
    """Schema for creating training packages"""
    code: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    release_date: Optional[datetime] = None
    xml_file: Optional[str] = None
    processed: Optional[str] = 'N'
    visible: Optional[bool] = True

class TrainingPackageUpdateSchema(BaseSchema):
    """Schema for updating training packages"""
    code: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    release_date: Optional[datetime] = None
    xml_file: Optional[str] = None
    processed: Optional[str] = None
    visible: Optional[bool] = None

class UserProfileSchema(BaseSchema):
    id: Optional[UUID] = None
    user_id: UUID
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    experience_points: int = 0
    level: int = 1

class UserProfileUpdateSchema(BaseSchema):
    """Schema for user profile updates - excludes id and user_id which shouldn't be directly updated"""
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    experience_points: Optional[int] = None
    level: Optional[int] = None

class UnitPerformanceCriteriaSchema(BaseSchema):
    """Schema for performance criteria within unit elements"""
    id: Optional[int] = None
    element_id: int
    unit_id: int
    pc_num: str
    pc_text: str

class UnitElementSchema(BaseSchema):
    """Schema for unit elements including performance criteria"""
    id: Optional[int] = None
    unit_id: int
    element_num: str
    element_text: str
    performance_criteria: Optional[List[UnitPerformanceCriteriaSchema]] = None

class UnitSchema(BaseSchema):
    id: Optional[int] = None
    code: str
    training_package_id: Optional[int]
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    release_date: Optional[datetime] = None
    xml_file: Optional[str] = None
    assessment_requirements_file: Optional[str] = None
    unit_descriptor: Optional[str] = None
    unit_application: Optional[str] = None
    licensing_information: Optional[str] = None
    unit_prerequisites: Optional[str] = None
    employability_skills: Optional[str] = None
    unit_elements: Optional[str] = None
    unit_required_skills: Optional[str] = None
    unit_evidence: Optional[str] = None
    unit_range: Optional[str] = None
    unit_sectors: Optional[str] = None
    unit_competency_field: Optional[str] = None
    unit_corequisites: Optional[str] = None
    unit_foundation_skills: Optional[str] = None
    performance_evidence: Optional[str] = None
    knowledge_evidence: Optional[str] = None
    assessment_conditions: Optional[str] = None
    nominal_hours: Optional[int] = None
    difficulty_level: int = 1
    experience_points: int = 100
    processed: str = 'N'
    visible: bool = True

class UnitCriticalAspectSchema(BaseSchema):
    """Schema for critical aspects of assessment"""
    id: Optional[int] = None
    unit_id: int
    section: str
    critical_aspect: str

class UnitRequiredSkillSchema(BaseSchema):
    """Schema for required skills in units"""
    id: Optional[int] = None
    unit_id: int
    skill_type: str
    skill_section: str
    skill_text: str

class QualificationSchema(BaseSchema):
    """Schema for qualifications"""
    id: Optional[int] = None
    code: str
    training_package_id: int
    title: str
    description: Optional[str] = None
    modification_history: Optional[str] = None
    pathways_information: Optional[str] = None
    licensing_information: Optional[str] = None
    entry_requirements: Optional[str] = None
    employability_skills: Optional[str] = None
    packaging_rules: Optional[str] = None
    unit_grid: Optional[str] = None
    release_date: Optional[datetime] = None
    xml_file: Optional[str] = None
    processed: str = 'N'
    visible: bool = True

class QualificationCreateSchema(BaseSchema):
    """Schema for creating qualifications"""
    code: str
    training_package_id: int
    title: str
    description: Optional[str] = None
    modification_history: Optional[str] = None
    pathways_information: Optional[str] = None
    licensing_information: Optional[str] = None
    entry_requirements: Optional[str] = None
    employability_skills: Optional[str] = None
    packaging_rules: Optional[str] = None
    unit_grid: Optional[str] = None
    release_date: Optional[datetime] = None
    xml_file: Optional[str] = None
    processed: Optional[str] = 'N'
    visible: Optional[bool] = True

class QualificationUpdateSchema(BaseSchema):
    """Schema for updating qualifications"""
    code: Optional[str] = None
    training_package_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    modification_history: Optional[str] = None
    pathways_information: Optional[str] = None
    licensing_information: Optional[str] = None
    entry_requirements: Optional[str] = None
    employability_skills: Optional[str] = None
    packaging_rules: Optional[str] = None
    unit_grid: Optional[str] = None
    release_date: Optional[datetime] = None
    xml_file: Optional[str] = None
    processed: Optional[str] = None
    visible: Optional[bool] = None

class SkillsetSchema(BaseSchema):
    """Schema for skillsets"""
    id: Optional[int] = None
    code: str
    training_package_id: int
    title: str
    description: Optional[str] = None
    target_group: Optional[str] = None
    statement_of_attainment: Optional[str] = None
    unit_grid: Optional[str] = None
    release_date: Optional[datetime] = None
    processed: str = 'N'
    visible: bool = True

class SkillsetCreateSchema(BaseSchema):
    """Schema for creating skillsets"""
    code: str
    training_package_id: int
    title: str
    description: Optional[str] = None
    target_group: Optional[str] = None
    statement_of_attainment: Optional[str] = None
    unit_grid: Optional[str] = None
    release_date: Optional[datetime] = None
    processed: Optional[str] = 'N'
    visible: Optional[bool] = True

class SkillsetUpdateSchema(BaseSchema):
    """Schema for updating skillsets"""
    code: Optional[str] = None
    training_package_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    target_group: Optional[str] = None
    statement_of_attainment: Optional[str] = None
    unit_grid: Optional[str] = None
    release_date: Optional[datetime] = None
    processed: Optional[str] = None
    visible: Optional[bool] = None

class AssessmentQuestionSchema(BaseSchema):
    """Schema for assessment questions"""
    id: Optional[int] = None
    assessment_id: int
    question_text: str
    question_type: str
    correct_answer: Optional[str] = None
    points: int = 10

class AssessmentQuestionCreateSchema(BaseSchema):
    """Schema for creating assessment questions"""
    assessment_id: int
    question_text: str
    question_type: str
    correct_answer: Optional[str] = None
    points: Optional[int] = 10

class AssessmentQuestionUpdateSchema(BaseSchema):
    """Schema for updating assessment questions"""
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    correct_answer: Optional[str] = None
    points: Optional[int] = None

class AssessmentSchema(BaseSchema):
    """Schema for assessments"""
    id: Optional[int] = None
    unit_id: int
    title: str
    description: Optional[str] = None
    type: str
    difficulty_level: int = 1
    experience_points: int = 50
    questions: Optional[List[AssessmentQuestionSchema]] = None

class AssessmentCreateSchema(BaseSchema):
    """Schema for creating assessments"""
    unit_id: int
    title: str
    description: Optional[str] = None
    type: str
    difficulty_level: Optional[int] = 1
    experience_points: Optional[int] = 50

class AssessmentUpdateSchema(BaseSchema):
    """Schema for updating assessments"""
    unit_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    difficulty_level: Optional[int] = None
    experience_points: Optional[int] = None

class UserSubmissionSchema(BaseSchema):
    """Schema for user assessment submissions"""
    id: Optional[int] = None
    assessment_id: int
    user_id: UUID
    status: str = 'pending'
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None

class UserProgressSchema(BaseSchema):
    """Schema for user progress tracking"""
    id: Optional[int] = None
    user_id: UUID
    unit_id: int
    status: str = 'not_started'
    progress_percentage: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class UserProgressCreateSchema(BaseSchema):
    """Schema for creating user progress records"""
    user_id: UUID
    unit_id: int
    status: str = 'not_started'
    progress_percentage: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class UserProgressUpdateSchema(BaseSchema):
    """Schema for updating user progress records"""
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AchievementSchema(BaseSchema):
    """Schema for achievements"""
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    experience_points: int = 100

class AchievementCreateSchema(BaseSchema):
    """Schema for creating achievements"""
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    experience_points: Optional[int] = 100

class AchievementUpdateSchema(BaseSchema):
    """Schema for updating achievements"""
    title: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    experience_points: Optional[int] = None

class UserAchievementSchema(BaseSchema):
    """Schema for user achievements"""
    id: Optional[int] = None
    user_id: UUID
    achievement_id: int
    awarded_at: datetime
    achievement: Optional[AchievementSchema] = None

class UserAchievementCreateSchema(BaseSchema):
    """Schema for creating user achievements"""
    user_id: UUID
    achievement_id: int
    awarded_at: Optional[datetime] = None

class BadgeSchema(BaseSchema):
    """Schema for badges"""
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

class BadgeCreateSchema(BaseSchema):
    """Schema for creating badges"""
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

class BadgeUpdateSchema(BaseSchema):
    """Schema for updating badges"""
    title: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None

class UserBadgeSchema(BaseSchema):
    """Schema for user badges"""
    id: Optional[int] = None
    user_id: UUID
    badge_id: int
    awarded_at: datetime
    badge: Optional[BadgeSchema] = None

class UserBadgeCreateSchema(BaseSchema):
    """Schema for creating user badges"""
    user_id: UUID
    badge_id: int
    awarded_at: Optional[datetime] = None

class RolePermissionSchema(BaseSchema):
    """Schema for role permissions"""
    role_id: int
    permission_id: int
    created_at: datetime
