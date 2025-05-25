"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-05-25 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create role_permissions table
    op.create_table('role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('experience_points', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('level', sa.Integer(), server_default=sa.text('1'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create training_packages table
    op.create_table('training_packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('release_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('xml_file', sa.String(length=255), nullable=True),
        sa.Column('processed', sa.String(length=1), server_default=sa.text("'N'"), nullable=True),
        sa.Column('visible', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create units table
    op.create_table('units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('training_package_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('release_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('xml_file', sa.String(length=255), nullable=True),
        sa.Column('assessment_requirements_file', sa.String(length=255), nullable=True),
        sa.Column('unit_descriptor', sa.Text(), nullable=True),
        sa.Column('unit_application', sa.Text(), nullable=True),
        sa.Column('licensing_information', sa.Text(), nullable=True),
        sa.Column('unit_prerequisites', sa.Text(), nullable=True),
        sa.Column('employability_skills', sa.Text(), nullable=True),
        sa.Column('unit_elements', sa.Text(), nullable=True),
        sa.Column('unit_required_skills', sa.Text(), nullable=True),
        sa.Column('unit_evidence', sa.Text(), nullable=True),
        sa.Column('unit_range', sa.Text(), nullable=True),
        sa.Column('unit_sectors', sa.Text(), nullable=True),
        sa.Column('unit_competency_field', sa.Text(), nullable=True),
        sa.Column('unit_corequisites', sa.Text(), nullable=True),
        sa.Column('unit_foundation_skills', sa.Text(), nullable=True),
        sa.Column('performance_evidence', sa.Text(), nullable=True),
        sa.Column('knowledge_evidence', sa.Text(), nullable=True),
        sa.Column('assessment_conditions', sa.Text(), nullable=True),
        sa.Column('nominal_hours', sa.Integer(), nullable=True),
        sa.Column('difficulty_level', sa.Integer(), server_default=sa.text('1'), nullable=True),
        sa.Column('experience_points', sa.Integer(), server_default=sa.text('100'), nullable=True),
        sa.Column('processed', sa.String(length=1), server_default=sa.text("'N'"), nullable=True),
        sa.Column('visible', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['training_package_id'], ['training_packages.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create qualifications table
    op.create_table('qualifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('training_package_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('modification_history', sa.Text(), nullable=True),
        sa.Column('pathways_information', sa.Text(), nullable=True),
        sa.Column('licensing_information', sa.Text(), nullable=True),
        sa.Column('entry_requirements', sa.Text(), nullable=True),
        sa.Column('employability_skills', sa.Text(), nullable=True),
        sa.Column('packaging_rules', sa.Text(), nullable=True),
        sa.Column('unit_grid', sa.Text(), nullable=True),
        sa.Column('release_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('xml_file', sa.String(length=255), nullable=True),
        sa.Column('processed', sa.String(length=1), server_default=sa.text("'N'"), nullable=True),
        sa.Column('visible', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['training_package_id'], ['training_packages.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create skillsets table
    op.create_table('skillsets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('training_package_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('modification_history', sa.Text(), nullable=True),
        sa.Column('pathways_information', sa.Text(), nullable=True),
        sa.Column('licensing_information', sa.Text(), nullable=True),
        sa.Column('entry_requirements', sa.Text(), nullable=True),
        sa.Column('target_group', sa.Text(), nullable=True),
        sa.Column('statement_of_attainment', sa.Text(), nullable=True),
        sa.Column('unit_grid', sa.Text(), nullable=True),
        sa.Column('release_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('xml_file', sa.String(length=255), nullable=True),
        sa.Column('processed', sa.String(length=1), server_default=sa.text("'N'"), nullable=True),
        sa.Column('visible', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['training_package_id'], ['training_packages.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create achievements table
    op.create_table('achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(length=255), nullable=True),
        sa.Column('experience_points', sa.Integer(), server_default=sa.text('100'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create badges table
    op.create_table('badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create assessments table
    op.create_table('assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), server_default=sa.text('1'), nullable=True),
        sa.Column('experience_points', sa.Integer(), server_default=sa.text('50'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unit_elements table
    op.create_table('unit_elements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('element_num', sa.String(length=50), nullable=True),
        sa.Column('element_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unit_critical_aspects table
    op.create_table('unit_critical_aspects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('section', sa.String(length=255), nullable=True),
        sa.Column('critical_aspect', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unit_required_skills table
    op.create_table('unit_required_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('skill_type', sa.String(length=100), nullable=True),
        sa.Column('skill_section', sa.String(length=255), nullable=True),
        sa.Column('skill_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_progress table
    op.create_table('user_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default=sa.text("'not_started'"), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'unit_id')
    )
    
    # Create user_achievements table
    op.create_table('user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('achievement_id', sa.Integer(), nullable=True),
        sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'achievement_id')
    )
    
    # Create user_badges table
    op.create_table('user_badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('badge_id', sa.Integer(), nullable=True),
        sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'badge_id')
    )
    
    # Create assessment_questions table
    op.create_table('assessment_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('correct_answer', sa.Text(), nullable=True),
        sa.Column('points', sa.Integer(), server_default=sa.text('10'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unit_performance_criteria table
    op.create_table('unit_performance_criteria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('element_id', sa.Integer(), nullable=True),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('pc_num', sa.String(length=50), nullable=True),
        sa.Column('pc_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['element_id'], ['unit_elements.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_submissions table
    op.create_table('user_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=True),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default=sa.text("'pending'"), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role_id', 'users', ['role_id'])
    op.create_index('idx_training_packages_code', 'training_packages', ['code'])
    op.create_index('idx_training_packages_title', 'training_packages', ['title'])
    op.create_index('idx_training_packages_status', 'training_packages', ['status'])
    op.create_index('idx_training_packages_release_date', 'training_packages', ['release_date'])
    op.create_index('idx_units_code', 'units', ['code'])
    op.create_index('idx_units_title', 'units', ['title'])
    op.create_index('idx_units_training_package_id', 'units', ['training_package_id'])
    op.create_index('idx_units_release_date', 'units', ['release_date'])
    op.create_index('idx_qualifications_code', 'qualifications', ['code'])
    op.create_index('idx_qualifications_title', 'qualifications', ['title'])
    op.create_index('idx_qualifications_training_package_id', 'qualifications', ['training_package_id'])
    op.create_index('idx_qualifications_release_date', 'qualifications', ['release_date'])
    op.create_index('idx_skillsets_code', 'skillsets', ['code'])
    op.create_index('idx_skillsets_title', 'skillsets', ['title'])
    op.create_index('idx_skillsets_training_package_id', 'skillsets', ['training_package_id'])
    op.create_index('idx_skillsets_release_date', 'skillsets', ['release_date'])
    op.create_index('idx_user_progress_user_id', 'user_progress', ['user_id'])
    op.create_index('idx_user_progress_unit_id', 'user_progress', ['unit_id'])
    op.create_index('idx_user_submissions_user_id', 'user_submissions', ['user_id'])
    op.create_index('idx_user_submissions_assessment_id', 'user_submissions', ['assessment_id'])
    op.create_index('idx_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('idx_user_badges_user_id', 'user_badges', ['user_id'])
    
    # Create full-text search indexes
    op.execute("CREATE INDEX idx_training_packages_fts ON training_packages USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')))")
    op.execute("CREATE INDEX idx_units_fts ON units USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || COALESCE(unit_descriptor, '') || ' ' || COALESCE(unit_application, '')))")
    op.execute("CREATE INDEX idx_qualifications_fts ON qualifications USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')))")
    op.execute("CREATE INDEX idx_skillsets_fts ON skillsets USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')))")
    
    # Create update trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create triggers for all tables
    tables_with_updated_at = [
        'roles', 'permissions', 'users', 'user_profiles', 'training_packages',
        'units', 'unit_elements', 'unit_performance_criteria', 'unit_critical_aspects',
        'unit_required_skills', 'qualifications', 'skillsets', 'user_progress',
        'assessments', 'assessment_questions', 'user_submissions', 'achievements',
        'user_achievements', 'badges', 'user_badges'
    ]
    
    for table in tables_with_updated_at:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    tables_with_updated_at = [
        'roles', 'permissions', 'users', 'user_profiles', 'training_packages',
        'units', 'unit_elements', 'unit_performance_criteria', 'unit_critical_aspects',
        'unit_required_skills', 'qualifications', 'skillsets', 'user_progress',
        'assessments', 'assessment_questions', 'user_submissions', 'achievements',
        'user_achievements', 'badges', 'user_badges'
    ]
    
    for table in tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop indexes
    op.drop_index('idx_user_badges_user_id')
    op.drop_index('idx_user_achievements_user_id')
    op.drop_index('idx_user_submissions_assessment_id')
    op.drop_index('idx_user_submissions_user_id')
    op.drop_index('idx_user_progress_unit_id')
    op.drop_index('idx_user_progress_user_id')
    op.drop_index('idx_skillsets_release_date')
    op.drop_index('idx_skillsets_training_package_id')
    op.drop_index('idx_skillsets_title')
    op.drop_index('idx_skillsets_code')
    op.drop_index('idx_qualifications_release_date')
    op.drop_index('idx_qualifications_training_package_id')
    op.drop_index('idx_qualifications_title')
    op.drop_index('idx_qualifications_code')
    op.drop_index('idx_units_release_date')
    op.drop_index('idx_units_training_package_id')
    op.drop_index('idx_units_title')
    op.drop_index('idx_units_code')
    op.drop_index('idx_training_packages_release_date')
    op.drop_index('idx_training_packages_status')
    op.drop_index('idx_training_packages_title')
    op.drop_index('idx_training_packages_code')
    op.drop_index('idx_users_role_id')
    op.drop_index('idx_users_email')
    
    # Drop full-text search indexes
    op.execute("DROP INDEX IF EXISTS idx_skillsets_fts")
    op.execute("DROP INDEX IF EXISTS idx_qualifications_fts")
    op.execute("DROP INDEX IF EXISTS idx_units_fts")
    op.execute("DROP INDEX IF EXISTS idx_training_packages_fts")
    
    # Drop tables in reverse order
    op.drop_table('user_submissions')
    op.drop_table('unit_performance_criteria')
    op.drop_table('assessment_questions')
    op.drop_table('user_badges')
    op.drop_table('user_achievements')
    op.drop_table('user_progress')
    op.drop_table('unit_required_skills')
    op.drop_table('unit_critical_aspects')
    op.drop_table('unit_elements')
    op.drop_table('assessments')
    op.drop_table('badges')
    op.drop_table('achievements')
    op.drop_table('skillsets')
    op.drop_table('qualifications')
    op.drop_table('units')
    op.drop_table('training_packages')
    op.drop_table('user_profiles')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    
    # Drop UUID extension
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
