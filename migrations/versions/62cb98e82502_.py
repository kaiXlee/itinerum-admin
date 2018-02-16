"""empty message

Revision ID: 62cb98e82502
Revises: 45d63624e49e
Create Date: 2018-02-13 20:38:48.723364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62cb98e82502'
down_revision = '45d63624e49e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('mobile_cancelled_prompt_responses', 'prompt_uuid',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)
    op.alter_column('mobile_prompt_responses', 'prompt_num',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('mobile_prompt_responses', 'prompt_uuid',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('mobile_prompt_responses', 'prompt_uuid',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)
    op.alter_column('mobile_prompt_responses', 'prompt_num',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('mobile_cancelled_prompt_responses', 'prompt_uuid',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)
    # ### end Alembic commands ###
