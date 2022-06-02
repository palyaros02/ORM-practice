from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://palyaros02:paSS123@localhost:5432/Shop_ORM',
    echo=False,
)

Session = sessionmaker(engine)

Base = declarative_base()
