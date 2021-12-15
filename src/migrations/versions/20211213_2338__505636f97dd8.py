"""Example init migration

Revision ID:505636f97dd8
Revises:
Create Date:2021-12-13 23:38:34.772642

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "505636f97dd8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "example",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("example")
    # ### end Alembic commands ###
