"""Updated on delete for all tables

Revision ID: d655bba8f562
Revises: 83a7cc0f2c33
Create Date: 2025-02-04 20:34:35.449390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd655bba8f562'
down_revision = '83a7cc0f2c33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.Enum('expense', 'revenue', name='transaction_type'),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.Enum('expense', 'revenue', name='transaction_type'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)

    # ### end Alembic commands ###
