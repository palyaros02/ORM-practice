import sqlalchemy as sa
from sqlalchemy import MetaData, select, and_
from sqlalchemy.dialects.postgresql.base import PGInspector

from config import Base, engine, Session
from orm.tables import *
from orm.insert import insert

from pprint import pprint


class Interface:
    __tables = dict(zip(
        ['магазины', 'районы', 'курьеры', 'покупатели', 'товары', 'заказы', 'статусы', 'лог'],
        ['shops', 'districts', 'couriers', 'clients', 'products', 'orders', 'statuses', 'logs']
    ))

    meta = Base.metadata
    meta.reflect(engine, 'public')

    inspector: PGInspector = sa.inspect(engine)

    selected_table_name = 'None'
    selected_table = sa.Table('', meta, comment='выберите таблицу')

    obj = None

    def tables_names(self):
        return [key.capitalize() for key in self.__tables.keys()]

    def use_table(self, table_name: str):
        self.selected_table_name = table_name
        self.selected_table = self.meta.tables.get('public.' + self.__tables[table_name])

    def show_table(self):
        print(f'Выбрана таблица {self.selected_table_name.capitalize()}: {self.selected_table.comment}')

    def get_columns(self):
        return list(zip(*self.selected_table.columns.items()))[0]

    def print_values(self, values):
        columns = self.get_columns()
        fs = '{:>20}'*len(columns)
        print(fs.format(*columns))
        for line in values:
            print(fs.format(*[str(x)[:19] for x in line]))

    def insert_value(self, values):
        with Session() as s:
            insert_stmt = sa.insert(self.selected_table).values(values)
            s.execute(insert_stmt)
            s.commit()

    def get_values(self,):
        with Session() as s:
            res = s.query(self.selected_table).all()
            self.print_values(res)

    def get_object(self, id):
        cls = self.table_to_class(self.__tables[self.selected_table_name])
        with Session() as s:
            self.obj = s.query(cls).filter(getattr(cls, cls.__name__.lower()+'_id') == id).one()

    def delete_obj(self):
        with Session() as s:
            s.delete(self.obj)
            self.obj = None
            s.commit()

    @staticmethod
    def table_to_class(name):
        res = None
        for mapper in Base.registry.mappers:
            if hasattr(mapper.class_, '__tablename__') and mapper.class_.__tablename__ == name:
                res =  mapper.class_
        if res:
            return res
        else:
            raise AttributeError('wrong table name')



