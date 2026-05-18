"""m2_quiz_mvp

Revision ID: fb4299563748
Revises: 3a9df4dc8028
Create Date: 2026-05-18 00:55:42.237713

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fb4299563748"
down_revision = "3a9df4dc8028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create new M2 tables
    op.create_table(
        "question_packs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("training_package_code", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("version", sa.String(length=100), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("question_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_element_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("element_id", sa.Integer(), nullable=False),
        sa.Column("unit_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=True),
        sa.Column("xp_awarded", sa.Integer(), nullable=True),
        sa.Column("passed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["element_id"],
            ["unit_elements.id"],
        ),
        sa.ForeignKeyConstraint(
            ["unit_id"],
            ["units.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "element_id", name="uq_user_element"),
    )
    op.create_table(
        "user_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("answer", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["assessment_questions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Drop the old user_submissions table (superseded by user_answers)
    op.drop_table("user_submissions")

    # Add new columns to assessment_questions
    op.add_column(
        "assessment_questions", sa.Column("pc_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "assessment_questions",
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "assessment_questions", sa.Column("source", sa.String(length=20), nullable=True)
    )
    op.add_column(
        "assessment_questions",
        sa.Column("review_status", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "assessment_questions", sa.Column("is_active", sa.Boolean(), nullable=True)
    )
    op.create_foreign_key(
        None, "assessment_questions", "unit_performance_criteria", ["pc_id"], ["id"]
    )

    # Add element_id to assessments
    op.add_column("assessments", sa.Column("element_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "assessments", "unit_elements", ["element_id"], ["id"])

    # Add code to badges
    op.add_column("badges", sa.Column("code", sa.String(length=50), nullable=True))
    op.create_unique_constraint(None, "badges", ["code"])

    # Add plain_english_description to units
    op.add_column(
        "units", sa.Column("plain_english_description", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("units", "plain_english_description")
    op.drop_constraint(None, "badges", type_="unique")
    op.drop_column("badges", "code")
    op.drop_constraint(None, "assessments", type_="foreignkey")
    op.drop_column("assessments", "element_id")
    op.drop_constraint(None, "assessment_questions", type_="foreignkey")
    op.drop_column("assessment_questions", "is_active")
    op.drop_column("assessment_questions", "review_status")
    op.drop_column("assessment_questions", "source")
    op.drop_column("assessment_questions", "options")
    op.drop_column("assessment_questions", "pc_id")
    op.drop_table("user_answers")
    op.drop_table("user_element_progress")
    op.drop_table("question_packs")
    op.create_table(
        "user_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("graded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
