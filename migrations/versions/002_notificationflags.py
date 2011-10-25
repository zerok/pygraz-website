from sqlalchemy import *
from migrate import *


meta = MetaData()

user_tbl = Table('user', meta)
status_col = Column('email_status', String, default='not_verified')
activation_code_col = Column('email_activation_code', String, nullable=True)
notify_new_meetup = Column('email_notify_new_meetup', Boolean, default=False)
notify_new_sessionidea = Column('email_notify_new_sessionidea', Boolean, default=False)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    user_tbl.create_column(status_col)
    user_tbl.create_column(activation_code_col)
    user_tbl.create_column(notify_new_meetup)
    user_tbl.create_column(notify_new_sessionidea)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    user_tbl.drop_column(status_col)
    user_tbl.drop_column(activation_code_col)
    user_tbl.drop_column(notify_new_meetup)
    user_tbl.drop_column(notify_new_sessionidea)
