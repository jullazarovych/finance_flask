"""Updated type column in transactions

Revision ID: 83a7cc0f2c33
Revises: bf21eed88287
Create Date: 2025-02-04 19:20:44.209388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83a7cc0f2c33'
down_revision = 'bf21eed88287'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_transaction',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('transaction_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'transaction_id')
    )
    op.create_table('transaction_categories',
    sa.Column('transaction_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
    sa.PrimaryKeyConstraint('transaction_id', 'category_id')
    )

def downgrade():
    
    op.drop_table('transaction_categories')
    op.drop_table('transactions')
    op.drop_table('user_transaction')
    # ### end Alembic commands ###
