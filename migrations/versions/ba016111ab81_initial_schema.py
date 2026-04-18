"""initial schema

Revision ID: ba016111ab81
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "ba016111ab81"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30)),
        sa.Column("lat", sa.Float()),
        sa.Column("lng", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "providers",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("address", sa.String(255)),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("verified", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("icon", sa.String(50)),
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("provider_id", sa.String(), sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("category_id", sa.String(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("avg_rating", sa.Float(), default=0.0),
        sa.Column("active", sa.Boolean(), default=True),
    )

    op.create_table(
        "time_slots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("activity_id", sa.String(), sa.ForeignKey("activities.id"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("booked", sa.Integer(), default=0),
    )

    op.create_table(
        "bookings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activity_id", sa.String(), sa.ForeignKey("activities.id"), nullable=False),
        sa.Column("time_slot_id", sa.String(), sa.ForeignKey("time_slots.id"), nullable=False),
        sa.Column("participants", sa.Integer(), default=1),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "cancelled", "completed", name="bookingstatus"),
            default="pending",
        ),
        sa.Column("booked_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activity_id", sa.String(), sa.ForeignKey("activities.id"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "wishlist",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activity_id", sa.String(), sa.ForeignKey("activities.id"), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("wishlist")
    op.drop_table("reviews")
    op.drop_table("bookings")
    op.drop_table("time_slots")
    op.drop_table("activities")
    op.drop_table("categories")
    op.drop_table("providers")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS bookingstatus")
