"""Add authentication OTP challenges."""
from alembic import op
import sqlalchemy as sa

revision = "a71c92d4e601"
down_revision = "e4ed0c56abd1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_otp_challenges",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=30), nullable=False),
        sa.Column("otp_hash", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_sent_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_auth_otp_challenges_email", "auth_otp_challenges", ["email"])
    op.create_index("ix_auth_otp_challenges_purpose", "auth_otp_challenges", ["purpose"])


def downgrade():
    op.drop_index("ix_auth_otp_challenges_purpose", table_name="auth_otp_challenges")
    op.drop_index("ix_auth_otp_challenges_email", table_name="auth_otp_challenges")
    op.drop_table("auth_otp_challenges")
