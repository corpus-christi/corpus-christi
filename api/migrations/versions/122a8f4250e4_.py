"""Added linking tables

Revision ID: 122a8f4250e4
Revises: 6bd142e99d95
Create Date: 2019-01-09 14:15:46.181114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '122a8f4250e4'
down_revision = '6bd142e99d95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events_team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events_eventasset',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('asset_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['asset_id'], ['events_asset.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['events_event.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'asset_id')
    )
    op.create_table('events_eventparticipant',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events_event.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['people_person.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'person_id')
    )
    op.create_table('events_eventperson',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events_event.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['people_person.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'person_id')
    )
    op.create_table('events_eventteam',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events_event.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['events_team.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'team_id')
    )
    op.create_table('events_teammember',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['member_id'], ['people_person.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['events_team.id'], ),
    sa.PrimaryKeyConstraint('team_id', 'member_id')
    )
    op.drop_table('events_teams')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events_teams',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), nullable=False),
    sa.Column('active', sa.BOOLEAN(), nullable=True),
    sa.CheckConstraint('active IN (0, 1)'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('events_teammember')
    op.drop_table('events_eventteam')
    op.drop_table('events_eventperson')
    op.drop_table('events_eventparticipant')
    op.drop_table('events_eventasset')
    op.drop_table('events_team')
    # ### end Alembic commands ###
