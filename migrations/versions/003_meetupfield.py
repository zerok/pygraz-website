from sqlalchemy import *
from migrate import *

meta = MetaData()

meetup_tbl = Table('meetup', meta)
meetupcom_id_col = Column('meetupcom_eventid', String, nullable=True)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    meetup_tbl.create_column(meetupcom_id_col)
    pass

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    meetup_tbl.drop_column(meetupcom_id_col)
    pass
