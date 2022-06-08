from app.interface import Interface

from config import Base, engine, Session
from orm.tables import *

from sqlalchemy.exc import NoResultFound

from pprint import pprint

if __name__ == '__main__':
    commands = """Команды:
    Команды - показать команды
    Таблицы - показать таблицы
    Выбрать {Название таблицы} - выбрать таблицу для манипуляций
    Записи - показать записи
    Запись {id} - выбрать конкретную запись и получить подробный вывод
    Добавить - ввести данные для добавления
    Удалить - удалить выбранную запись
    Выход"""

    interface = Interface()

    print(commands)
    while True:
        ans = input('>>> ').lower()
        match ans.split():
            case 'команды',:
                print(commands)
            case 'таблицы',:
                print(interface.tables_names())
            case 'выбрать', table:
                try:
                    interface.use_table(table)
                    interface.show_table()
                except:
                    print('Нет такой таблицы, попробуйте снова')
            case 'записи',:
                if interface.selected_table_name == 'None':
                    interface.show_table()
                    continue
                interface.get_values()
            case 'запись', id:
                try:
                    interface.get_object(id)
                    obj = interface.obj
                except NoResultFound:
                    print('Нет такого объекта, попробуйте снова')
                    continue
                if obj is not None:
                    print(f'Выбран объект {obj}')
                    if not isinstance(obj, Log):
                        with Session() as s:
                            s.query(obj.__class__).where(obj.__class__ == obj)
                            pprint(obj.get_info())
            case 'добавить',:
                if interface.selected_table_name == 'None':
                    interface.show_table()
                    continue
                values = dict()
                columns = interface.get_columns()
                try:
                    for col in columns:
                        values[col] = input(f'{col} = ')
                    interface.insert_value(values)
                except:
                    print('Произошла ошибка, попробуйте еще раз')
            case 'удалить',:
                if interface.selected_table_name == 'None':
                    interface.show_table()
                    continue
                if interface.obj is None:
                    print("Выберите запись")
                else:
                    interface.delete_obj()
            case 'выход',:
                break
            case _:
                print('Нет такой команды')
