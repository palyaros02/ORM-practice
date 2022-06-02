import cmd

import sqlalchemy as sa

from config import Base, engine, Session

meta = Base.metadata
meta.reflect(bind=engine, schema='public')

inspector = sa.inspect(engine)

print(inspector.get_table_names())

tables = dict(zip(
    ['Магазины', 'Районы', 'Курьеры', 'Клиенты', 'Товары', 'Заказы', 'Статусы'],
    ['shops', 'districts', 'couriers', 'clients', 'products', 'orders', 'statuses']
))
"""
Команды:
Таблицы
Выбрать [Название таблицы]
Записи [-количество]
Добавить (запись)
Удалить (запись)
Поиск"""

if __name__ == '__main__':
    pass
