"""create auth table

Revision ID: d9ac92ba8eb5
Revises:
Create Date: 2024-06-12 20:57:27.682196

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "d9ac92ba8eb5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("tfa_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_full_name"), "user", ["full_name"], unique=False)
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_table(
        "device",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=True),
        sa.Column("device_type", postgresql.ENUM("EMAIL", "CODE_GENERATOR", name="devicetypeenum"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_device_id"), "device", ["id"], unique=False)
    op.create_index(op.f("ix_device_key"), "device", ["key"], unique=False)
    op.create_table(
        "backuptoken",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("token", sa.String(length=8), nullable=True),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["device.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backuptoken_id"), "backuptoken", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_backuptoken_id"), table_name="backuptoken")
    op.drop_table("backuptoken")
    op.drop_index(op.f("ix_device_key"), table_name="device")
    op.drop_index(op.f("ix_device_id"), table_name="device")
    op.drop_table("device")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_full_name"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
