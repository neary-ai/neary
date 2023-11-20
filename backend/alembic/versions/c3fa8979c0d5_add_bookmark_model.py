"""Add bookmark model

Revision ID: c3fa8979c0d5
Revises: feafafa7998e
Create Date: 2023-11-18 09:58:26.667402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3fa8979c0d5"
down_revision: Union[str, None] = "feafafa7998e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "bookmark_model",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("message_id", sa.Integer, sa.ForeignKey("message_model.id")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade():
    op.drop_table("bookmark_model")
