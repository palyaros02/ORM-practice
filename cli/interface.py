import sqlalchemy as sa

from config import Base, engine

meta = Base.metadata
meta.reflect(bind=engine, schema='public')

inspector = sa.inspect(engine)

# print(meta.tables.keys())
print(inspector.get_table_names())

tables = dict(zip(
    ['Магазины', 'Районы', 'Курьеры', 'Клиенты', 'Товары', 'Заказы', 'Статусы'],
    ['shops', 'districts', 'couriers', 'clients', 'products', 'orders', 'statuses']
))

if __name__ == '__main__':
    pass
