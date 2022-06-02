import cmd

import sqlalchemy as sa

from config import Base, engine, Session

# meta = Base.metadata
# meta.reflect(bind=engine, schema='public')
#
# inspector = sa.inspect(engine)

# print(inspector.get_table_names())

tables = dict(zip(
    ['Магазины', 'Районы', 'Курьеры', 'Клиенты', 'Товары', 'Заказы', 'Статусы'],
    ['shops', 'districts', 'couriers', 'clients', 'products', 'orders', 'statuses']
))

if __name__ == '__main__':
    from orm.tables import *
    from orm.insert import *

    insert()

    commands = """Команды:
    Команды - показать команды
    Таблицы - показать таблицы
    Выбрать [Название таблицы] - выбрать таблицу для манипуляций
    Записи [-количество] - показать записи из таблицы
    Добавить (запись)
    Удалить (запись)
    Выход"""
    selected_table = 'Не выбрана'
    print(commands)
    while True:
        ans = input()
        match ans:
            case 'Команды':
                print(commands)




