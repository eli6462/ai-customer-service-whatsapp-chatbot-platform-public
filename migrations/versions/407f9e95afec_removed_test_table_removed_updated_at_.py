"""removed test table. removed 'updated_at' in the CommonDetails model, and commented out the 'create_at' property.

Revision ID: 407f9e95afec
Revises: ee9e88c4cabc
Create Date: 2024-07-18 05:07:34.169434

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '407f9e95afec'
down_revision = 'ee9e88c4cabc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_table')
    with op.batch_alter_table('ai_assistant', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')

    with op.batch_alter_table('business', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')

    with op.batch_alter_table('business_client', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')

    with op.batch_alter_table('business_credentials', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')

    with op.batch_alter_table('slack_user_ids', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('slack_user_ids', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', mysql.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('created_at', mysql.DATETIME(), nullable=False))

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', mysql.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('created_at', mysql.DATETIME(), nullable=False))

    with op.batch_alter_table('business_credentials', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', mysql.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('created_at', mysql.DATETIME(), nullable=False))

    with op.batch_alter_table('business_client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', mysql.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('created_at', mysql.DATETIME(), nullable=False))

    with op.batch_alter_table('business', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', mysql.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('created_at', mysql.DATETIME(), nullable=False))

    with op.batch_alter_table('ai_assistant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', mysql.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('created_at', mysql.DATETIME(), nullable=False))

    op.create_table('test_table',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('created_at_test', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at_test', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
