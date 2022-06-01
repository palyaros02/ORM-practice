import sqlalchemy as sa
from orm.insert import *

import sqlalchemy as sa

meta = sa.MetaData(bind=engine)

print(sa.schema.MetaData.tables)
