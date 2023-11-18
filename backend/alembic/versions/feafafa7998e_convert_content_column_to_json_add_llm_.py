"""Convert content column to JSON, add LLM table

Revision ID: feafafa7998e
Revises: 2a4309568eba
Create Date: 2023-11-16 22:43:36.984314

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import select, table, column


# revision identifiers, used by Alembic.
revision: str = "feafafa7998e"
down_revision: Union[str, None] = "2a4309568eba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create a new temporary column to store the JSON data
    op.add_column("message_model", sa.Column("content_json", sa.JSON(), nullable=True))

    # Define a temporary table to run update statements against
    message_model = table(
        "message_model",
        column("id", sa.Integer),
        column("content", sa.Text),
        column("content_json", sa.JSON),
    )

    # Retrieve the connection to execute raw SQL
    conn = op.get_bind()

    # Select all messages with old format content
    result = conn.execute(select(message_model.c.id, message_model.c.content))

    # Iterate over each row and update the new 'content_json' column with JSON format
    for row in result:
        content = row.content
        if content is not None:
            new_content = {"text": content}
            conn.execute(
                message_model.update()
                .where(
                    message_model.c.id
                    == row.id  # Access id using column name as string
                )
                .values(content_json=new_content)
            )

    # Step 2: Drop the old 'content' column
    op.drop_column("message_model", "content")

    # Step 3: Rename the 'content_json' column to 'content'
    op.alter_column("message_model", "content_json", new_column_name="content")


def downgrade() -> None:
    pass
