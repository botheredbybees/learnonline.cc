from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Role(Base, TimestampMixin):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    users = relationship("User", back_populates="role")

class Permission(Base, TimestampMixin):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    
    id = Column(PGUUID, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role_id = Column(Integer, ForeignKey('roles.id'))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    
    role = relationship("Role", back_populates="users")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    progress = relationship("UserProgress", back_populates="user")
    submissions = relationship("UserSubmission", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")

class UserProfile(Base, TimestampMixin):
    __tablename__ = 'user_profiles'
    
    id = Column(PGUUID, primary_key=True)
    user_id = Column(PGUUID, ForeignKey('users.id'))
    avatar_url = Column(String(255))
    bio = Column(Text)
    experience_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    
    user = relationship("User", back_populates="profile")

class TrainingPackage(Base, TimestampMixin):
    __tablename__ = 'training_packages'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    status = Column(String(50))
    release_date = Column(DateTime(timezone=True))
    xml_file = Column(String(255))
    processed = Column(String(1), default='N')
    visible = Column(Boolean, default=True)
    
    units = relationship("Unit", back_populates="training_package")
    qualifications = relationship("Qualification", back_populates="training_package")
    skillsets = relationship("Skillset", back_populates="training_package")

class Unit(Base, TimestampMixin):
    __tablename__ = 'units'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    training_package_id = Column(Integer, ForeignKey('training_packages.id'))
    title = Column(Text, nullable=False)
    description = Column(Text)
    status = Column(String(50))
    release_date = Column(DateTime(timezone=True))
    xml_file = Column(String(255))
    assessment_requirements_file = Column(String(255))
    unit_descriptor = Column(Text)
    unit_application = Column(Text)
    licensing_information = Column(Text)
    unit_prerequisites = Column(Text)
    employability_skills = Column(Text)
    unit_elements = Column(Text)
    unit_required_skills = Column(Text)
    unit_evidence = Column(Text)
    unit_range = Column(Text)
    unit_sectors = Column(Text)
    unit_competency_field = Column(Text)
    unit_corequisites = Column(Text)
    unit_foundation_skills = Column(Text)
    performance_evidence = Column(Text)
    knowledge_evidence = Column(Text)
    assessment_conditions = Column(Text)
    nominal_hours = Column(Integer)
    difficulty_level = Column(Integer, default=1)
    experience_points = Column(Integer, default=100)
    processed = Column(String(1), default='N')
    visible = Column(Boolean, default=True)
    
    training_package = relationship("TrainingPackage", back_populates="units")
    elements = relationship("UnitElement", back_populates="unit")
    performance_criteria = relationship("UnitPerformanceCriteria", back_populates="unit")
    critical_aspects = relationship("UnitCriticalAspect", back_populates="unit")
    required_skills = relationship("UnitRequiredSkill", back_populates="unit")
    assessments = relationship("Assessment", back_populates="unit")
    user_progress = relationship("UserProgress", back_populates="unit")

class UnitElement(Base, TimestampMixin):
    __tablename__ = 'unit_elements'
    
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('units.id'))
    element_num = Column(String(50))
    element_text = Column(Text, nullable=False)
    
    unit = relationship("Unit", back_populates="elements")
    performance_criteria = relationship("UnitPerformanceCriteria", back_populates="element")

class UnitPerformanceCriteria(Base, TimestampMixin):
    __tablename__ = 'unit_performance_criteria'
    
    id = Column(Integer, primary_key=True)
    element_id = Column(Integer, ForeignKey('unit_elements.id'))
    unit_id = Column(Integer, ForeignKey('units.id'))
    pc_num = Column(String(50))
    pc_text = Column(Text, nullable=False)
    
    element = relationship("UnitElement", back_populates="performance_criteria")
    unit = relationship("Unit", back_populates="performance_criteria")

class UnitCriticalAspect(Base, TimestampMixin):
    __tablename__ = 'unit_critical_aspects'
    
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('units.id'))
    section = Column(String(255))
    critical_aspect = Column(Text, nullable=False)
    
    unit = relationship("Unit", back_populates="critical_aspects")

class UnitRequiredSkill(Base, TimestampMixin):
    __tablename__ = 'unit_required_skills'
    
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('units.id'))
    skill_type = Column(String(100))
    skill_section = Column(String(255))
    skill_text = Column(Text, nullable=False)
    
    unit = relationship("Unit", back_populates="required_skills")

class Qualification(Base, TimestampMixin):
    __tablename__ = 'qualifications'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    training_package_id = Column(Integer, ForeignKey('training_packages.id'))
    title = Column(Text, nullable=False)
    description = Column(Text)
    modification_history = Column(Text)
    pathways_information = Column(Text)
    licensing_information = Column(Text)
    entry_requirements = Column(Text)
    employability_skills = Column(Text)
    packaging_rules = Column(Text)
    unit_grid = Column(Text)
    release_date = Column(DateTime(timezone=True))
    xml_file = Column(String(255))
    processed = Column(String(1), default='N')
    visible = Column(Boolean, default=True)
    
    training_package = relationship("TrainingPackage", back_populates="qualifications")

class Skillset(Base, TimestampMixin):
    __tablename__ = 'skillsets'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    training_package_id = Column(Integer, ForeignKey('training_packages.id'))
    title = Column(Text, nullable=False)
    description = Column(Text)
    modification_history = Column(Text)
    pathways_information = Column(Text)
    licensing_information = Column(Text)
    entry_requirements = Column(Text)
    target_group = Column(Text)
    statement_of_attainment = Column(Text)
    unit_grid = Column(Text)
    release_date = Column(DateTime(timezone=True))
    xml_file = Column(String(255))
    processed = Column(String(1), default='N')
    visible = Column(Boolean, default=True)
    
    training_package = relationship("TrainingPackage", back_populates="skillsets")

class UserProgress(Base, TimestampMixin):
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(PGUUID, ForeignKey('users.id'))
    unit_id = Column(Integer, ForeignKey('units.id'))
    status = Column(String(50), default='not_started')
    progress_percentage = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="progress")
    unit = relationship("Unit", back_populates="user_progress")

class Assessment(Base, TimestampMixin):
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('units.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False)
    difficulty_level = Column(Integer, default=1)
    experience_points = Column(Integer, default=50)
    
    unit = relationship("Unit", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment")
    submissions = relationship("UserSubmission", back_populates="assessment")

class AssessmentQuestion(Base, TimestampMixin):
    __tablename__ = 'assessment_questions'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    correct_answer = Column(Text)
    points = Column(Integer, default=10)
    
    assessment = relationship("Assessment", back_populates="questions")

class UserSubmission(Base, TimestampMixin):
    __tablename__ = 'user_submissions'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    user_id = Column(PGUUID, ForeignKey('users.id'))
    status = Column(String(50), default='pending')
    score = Column(Integer)
    feedback = Column(Text)
    submitted_at = Column(DateTime(timezone=True), default=func.now())
    graded_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="submissions")
    assessment = relationship("Assessment", back_populates="submissions")

class Achievement(Base, TimestampMixin):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    experience_points = Column(Integer, default=100)
    
    user_achievements = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base, TimestampMixin):
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(PGUUID, ForeignKey('users.id'))
    achievement_id = Column(Integer, ForeignKey('achievements.id'))
    awarded_at = Column(DateTime(timezone=True), default=func.now())
    
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class Badge(Base, TimestampMixin):
    __tablename__ = 'badges'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    
    user_badges = relationship("UserBadge", back_populates="badge")

class UserBadge(Base, TimestampMixin):
    __tablename__ = 'user_badges'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(PGUUID, ForeignKey('users.id'))
    badge_id = Column(Integer, ForeignKey('badges.id'))
    awarded_at = Column(DateTime(timezone=True), default=func.now())
    
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")
