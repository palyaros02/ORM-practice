import sqlalchemy as sa
from sqlalchemy import event, DDL
from datetime import datetime, time
from random import randint

from orm.tables import *
from config import Base, engine, Session


def insert():
    Base.metadata.drop_all(engine)
    triggers = DDL("""
    CREATE OR REPLACE FUNCTION log()
    RETURNS trigger AS $body$
    BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
       INSERT INTO logs (change_date, operation_type, table_name)
       VALUES(CURRENT_TIMESTAMP, TG_OP, TG_TABLE_NAME);
       RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
       INSERT INTO logs (change_date, operation_type, table_name)
       VALUES(CURRENT_TIMESTAMP, 'DELETE', TG_TABLE_NAME);
       RETURN OLD;
    END IF;
    END;
    $body$ LANGUAGE plpgsql;
    
    CREATE TRIGGER orders_log
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION log();
    
    CREATE TRIGGER clients_log
    AFTER INSERT OR UPDATE OR DELETE ON clients
    FOR EACH ROW EXECUTE FUNCTION log();
    
    CREATE TRIGGER products_log
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION log();
    
    CREATE TRIGGER shops_log
    AFTER INSERT OR UPDATE OR DELETE ON shops
    FOR EACH ROW EXECUTE FUNCTION log();
    
    CREATE TRIGGER couriers_log
    AFTER INSERT OR UPDATE OR DELETE ON couriers
    FOR EACH ROW EXECUTE FUNCTION log();
    
    CREATE TRIGGER districts_log
    AFTER INSERT OR UPDATE OR DELETE ON districts
    FOR EACH ROW EXECUTE FUNCTION log();""")
    event.listen(Base.metadata, 'after_create', triggers.execute_if(dialect='postgresql'))

    Base.metadata.create_all(engine)

    districts = list(map(District, [
        'Академический', 'Алексеевский', 'Алтуфьевский', 'Арбат', 'Аэропорт', 'Бабушкинский', 'Басманный', 'Беговой',
        'Бескудниковский', 'Бибирево', 'Бирюлёво Восточное', 'Бирюлёво Западное', 'Богородское', 'Братеево',
        'Бутово Северное', 'Бутово Южное', 'Бутырский', 'Вешняки', 'Внуково', 'Войковский', 'Восточный',
        'Выхино-Жулебино', 'Гагаринский', 'Головинский', 'Гольяново', 'Даниловский', 'Дегунино Восточное',
        'Дегунино Западное', 'Дмитровский', 'Донской', 'Дорогомилово', 'Замоскворечье', 'Зюзино', 'Зябликово',
        'Ивановское', 'Измайлово Восточное', 'Измайлово', 'Измайлово Северное', 'Капотня', 'Коньково', 'Коптево',
        'Косино-Ухтомский', 'Котловка', 'Красносельский', 'Крылатское', 'Крюково', 'Кузьминки', 'Кунцево', 'Куркино',
        'Левобережный', 'Лефортово', 'Лианозово', 'Ломоносовский', 'Лосиноостровский', 'Люблино', 'Марфино',
        'Марьина роща', 'Марьино', 'Матушкино', 'Медведково Северное', 'Медведково Южное', 'Метрогородок',
        'Мещанский', 'Митино', 'Можайский', 'Молжаниновский', 'Москворечье-Сабурово', 'Нагатино-Садовники',
        'Нагатинский затон', 'Нагорный', 'Некрасовка', 'Нижегородский', 'Ново-Переделкино', 'Новогиреево',
        'Новокосино', 'Обручевский', 'Орехово-Борисово Северное', 'Орехово-Борисово Южное', 'Останкинский',
        'Отрадное', 'Очаково-Матвеевское', 'Перово', 'Печатники', 'Покровское-Стрешнево', 'Преображенское',
        'Пресненский', 'Проспект Вернадского', 'Раменки', 'Ростокино', 'Рязанский', 'Савёлки', 'Савёловский',
        'Свиблово', 'Северный', 'Силино', 'Сокол', 'Соколиная гора', 'Сокольники', 'Солнцево', 'Старое Крюково',
        'Строгино', 'Таганский', 'Тверской', 'Текстильщики', 'Тёплый Стан', 'Тимирязевский', 'Тропарёво-Никулино',
        'Тушино Северное', 'Тушино Южное', 'Филёвский парк', 'Фили-Давыдково', 'Хамовники', 'Ховрино',
        'Хорошёво-Мневники', 'Хорошёвский', 'Царицыно', 'Черёмушки', 'Чертаново Северное', 'Чертаново Центральное',
        'Чертаново Южное', 'Щукино', 'Южнопортовый', 'Якиманка', 'Ярославский', 'Ясенево']))

    statuses = list(map(Status, [
        'Создан', 'Оплачен', 'Собран', 'Передан в доставку', 'Доставлен']))

    shops = list(map(Shop, [
        'Рога и Копыта', 'Эльдорадо', 'У Петровича']))

    couriers = [
        ('Pauly', 'Higgen', '4075096814'),
        ('Dre', 'Finnes', '9994922979'),
        ('Denis', 'Portis', '5715044617'),
        ('Georges', 'Iannetti', '1184784718'),
        ('Annemarie', 'Topham', '7585643810'),
        ('Berkie', 'Benka', '5753291204'),
        ('Baily', 'Doole', '6347544174'),
        ('Cleavland', 'Cronshaw', '5403015835'),
        ('Rowe', 'Schultze', '5612134981'),
        ('Neda', 'Shefton', '8087398014')]
    couriers = [Courier(*courier) for courier in couriers]

    products = [
        ('Appetizer - Smoked Salmon / Dill', 290.83, 69),
        ('Clams - Bay', 693.39, 20),
        ('Mushrooms - Honey', 195.44, 39),
        ('Yogurt - Cherry, 175 Gr', 83.34, 17),
        ('Venison - Liver', 988.93, 20),
        ('Wine - Barolo Fontanafredda', 450.78, 11),
        ('Wine - Red, Gamay Noir', 792.18, 48),
        ('Soup Campbells', 538.72, 52),
        ('Amarula Cream', 31.13, 82),
        ('Lychee', 819.37, 95),
        ('Schnappes Peppermint - Walker', 962.96, 24),
        ('Shrimp - 21/25, Peel And Deviened', 39.62, 92),
        ('Fib N9 - Prague Powder', 261.2, 57),
        ('Puree - Kiwi', 650.04, 43),
        ('Filling - Mince Meat', 649.02, 19),
        ('Chip - Potato Dill Pickle', 485.11, 37),
        ('Spice - Peppercorn Melange', 521.82, 35),
        ('Scallops - 10/20', 443.44, 59),
        ('Fish - Bones', 113.59, 74),
        ('Island Oasis - Magarita Mix', 281.79, 5)]

    clients = [
        ('Arleyne', 'Crotch', '4249328283', '31739 Scott Drive', districts[8]),
        ('Vinny', 'Buckingham', '4313988521', '5 Rowland Street', districts[10]),
        ('Kellia', 'Pakeman', '1071536087', '022 Westend Center', districts[9]),
        ('Elnora', 'Fallows', '1371280446', '40 Eliot Trail', districts[6]),
        ('Travis', 'Liptrod', '4746859534', '61059 Grim Way', districts[4]),
        ('Phillipp', 'Havock', '1244803317', '865 Hovde Trail', districts[6]),
        ('Clarine', 'Canero', '2103286631', '52084 Anhalt Pass', districts[9]),
        ('Nickolaus', 'West', '2106108169', '582 Ludington Hill', districts[5]),
        ('Benni', 'Youel', '1203091967', '85331 Mcbride Street', districts[1]),
        ('Clarissa', 'Dutson', '1887254030', '05 Anzinger Alley', districts[3]),
        ('Germain', 'Winney', '7971153671', '7 Sullivan Court', districts[1]),
        ('Effie', 'Livingston', '9604413203', '587 Summer Ridge Lane', districts[2]),
        ('Orlando', 'McGoldrick', '7617674904', '423 Sage Hill', districts[5]),
        ('Yetta', 'Whettleton', '3943583403', '3 Shelley Road', districts[9]),
        ('Britt', 'Kaye', '9697865395', '7472 Merry Drive', districts[9])]
    clients = [Client(*client) for client in clients]

    with Session() as session:
        session.add_all(statuses)
        session.add_all(districts)
        session.add_all(shops)
        session.add_all(couriers)

        for d, t in zip(districts[:3], [time(1, 15), time(2, 25), time(3, 0)]):
            shops[0].add_district(d, t)

        for d, t in zip(districts[:7:2], [time(2, 15), time(5, 30), time(2, 0)]):
            shops[1].add_district(d, t)

        for d, t in zip(districts[1:7:2], [time(4, 15), time(2, 30), time(1, 15)]):
            shops[2].add_district(d, t)

        for courier in couriers[:3]:
            shops[0].add_courier(courier)

        for courier in couriers[3:6]:
            shops[1].add_courier(courier)

        for courier in couriers[6:]:
            shops[2].add_courier(courier)

        for shop in shops:
            for _ in range(randint(2, 7)):
                session.add(Product(*products[randint(1, len(products)-1)], shop))

        session.add_all(clients)
        orders = []
        for client in clients:
            shop = shops[randint(0, 2)]
            orders.append(
                Order(client, shop, shop.couriers[randint(0, len(shop.couriers) - 1)]))

        for order in orders:
            for i in range(randint(0, 5)):
                order.add_product(order.shop.products[randint(0, len(order.shop.products) - 1)], randint(0, 5))

        session.commit()


if __name__ == '__main__':
    insert()