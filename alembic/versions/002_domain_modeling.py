"""Domain modeling

Revision ID: 002
Revises: 001
Create Date: 2026-07-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)

    # 2. Create orders table
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Add category_id to products
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        
    # 4. Migrate data
    op.execute(
        "INSERT INTO categories (name) "
        "SELECT DISTINCT category FROM products WHERE category IS NOT NULL"
    )
    op.execute(
        "UPDATE products "
        "SET category_id = (SELECT id FROM categories WHERE categories.name = products.category)"
    )

    # 5. Drop old category column, add FK, change price type
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_index('ix_products_category')
        batch_op.drop_column('category')
        # In SQLite, adding a foreign key via alter table can be tricky but batch_op handles recreating the table
        batch_op.create_foreign_key('fk_product_category', 'categories', ['category_id'], ['id'])
        batch_op.alter_column('price',
               existing_type=sa.Float(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(), nullable=True))
        # Note: SQLite batch alter might complain about dropping FK by name if it wasn't named in the first place, 
        # but we named it 'fk_product_category' during upgrade.
        batch_op.drop_constraint('fk_product_category', type_='foreignkey')
        batch_op.alter_column('price',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.Float(),
               existing_nullable=True)
               
    op.execute(
        "UPDATE products "
        "SET category = (SELECT name FROM categories WHERE categories.id = products.category_id)"
    )
    
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_products_category'), ['category'], unique=False)
        batch_op.drop_column('category_id')

    op.drop_table('orders')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
