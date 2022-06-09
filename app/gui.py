import PySimpleGUI as sg
import re
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import object_session

import traceback
from config import Base, engine, Session
from orm.tables import *


def client_window(client: Client):
    def update_client_window(client: Client):
        session = object_session(client)
        districts = list(zip(*session.query(District.district_name).all()))[0]
        texts = sg.Column([
            [sg.Text('Имя')],
            [sg.Text('Фамилия')],
            [sg.Text('Телефон')],
            [sg.Text('Район')],
            [sg.Text('Адрес')],
            [],
        ], element_justification='r')
        fields = sg.Column([
            [sg.Input(key='FIRSTNAME', default_text=client.first_name, size=(20, 1))],
            [sg.Input(key='LASTNAME', default_text=client.last_name,size=(20, 1))],
            [sg.Input(key='PHONE', default_text=client.phone_number,size=(20, 1))],
            [sg.Combo(values=districts, default_value=client.district.district_name, key='DISTRICT', size=(20, 1))],
            [sg.Multiline(key='ADDRESS', default_text=client.address,no_scrollbar=True, size=(20, 2))],
        ], element_justification='l')
        layout = [
            [texts, fields],
            [sg.OK('OK'), sg.Stretch(), sg.Cancel('Отмена', key='EXIT')]
        ]
        window = sg.Window('Редактирование', layout, element_justification='c', modal=True)
        while True:
            event, values = window.read(timeout=100)
            match event:
                case sg.WIN_CLOSED | 'EXIT':
                    session.rollback()
                    session.commit()
                    break
                case 'OK':
                    err_msg = ''
                    if not re.match(r'^[+]?[(]?\d{3}[)]?[-\s\.]?\d{3}[-\s\.]?\d{4,6}$',  # regex for phones
                                    values['PHONE']):
                        err_msg += "Неверный формат номера!\n"
                    if err_msg:
                        sg.popup(err_msg)
                    else:
                        try:
                            session = object_session(client)
                            district = session.query(District). \
                                filter(District.district_name == values['DISTRICT']).one()
                            client.first_name = values['FIRSTNAME'].capitalize()
                            client.last_name = values['LASTNAME'].capitalize()
                            client.phone_number = values['PHONE']
                            client.address = values['ADDRESS']
                            client.district = district
                            session.commit()
                            break
                        except:
                            print(traceback.format_exc())
                            sg.popup('Неверно введены данные', title='Ошибка!')
        window.close()

    session = object_session(client)
    def get_order_values():
        return sorted([[o.order_id, o.shop.shop_name if o.shop else '', o.purchase_date.isoformat(' ')[:16],
                 o.price, o.status.status_name] for o in client.orders], key=lambda x: x[0])
    l_col = sg.Column([
        [sg.Table(values=get_order_values(), headings=['ID', 'Магазин', 'Дата', 'Сумма', 'Статус'],
                  auto_size_columns=False, enable_events=True,
                  col_widths=[3, 10, 12, 7, 8], key='ORDERS_TABLE')]
    ])
    r_col = sg.Column([
        [sg.Button('Показать выбранный', key='SHOW_ORDER')],
        [sg.Button('Оплатить', key='PAY_ORDER', disabled=False)],
        [sg.Button('Новый заказ', key='NEW_ORDER')],
        [sg.Button('Удалить', key='DELETE_ORDER')],
    ], element_justification='c')
    layout = [
        [sg.Frame(f'Покупатель [ ID: {client.client_id} ]', [
            [sg.Text(f'{client.first_name} {client.last_name},'), sg.Text(f'Тел.:{client.phone_number}', key='PHONE'),
             sg.Text(f'Адрес: {client.address}'), sg.Stretch(), sg.Button('Изм. данные', key='CHANGE_DATA')],
            [sg.HorizontalSeparator(pad=(0, 10))],
            [sg.Text('Заказы', font='14'), sg.Stretch()],
            [l_col, sg.VerticalSeparator(), r_col],
            [sg.HorizontalSeparator()],
            [sg.Exit('Выход', key='EXIT'), sg.Stretch()]
        ], element_justification='c', font='bold', key='FRAME')]
    ]
    window = sg.Window(f'Покупатель {client.first_name} {client.last_name}', layout, element_justification='c',
                       modal=True, finalize=True)
    reset = False
    while True:
        event, values = window.read(timeout=100)
        match event:
            case 'EXIT' | sg.WIN_CLOSED:
                reset = False
                session.commit()
                break
            case 'CHANGE_DATA':
                update_client_window(client)
                reset = True
                break
            case 'SHOW_ORDER':
                order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                order = list(filter(lambda order: order.order_id == order_data[0], client.orders))[0]
                try:
                    order_window(order, client=client, show=True)
                    window['ORDERS_TABLE'].update(values=get_order_values())
                except:
                    print(traceback.format_exc())
                window['ORDERS_TABLE'].update(values=get_order_values())
            case 'NEW_ORDER':
                try:
                    order = Order(date=datetime.now(), client=client)
                    session.add(order)
                    order_window(order, client=client)
                except:
                    print(traceback.format_exc())
                window['ORDERS_TABLE'].update(values=get_order_values())
            case 'ORDERS_TABLE':
                try:
                    order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                    order = list(filter(lambda order: order.order_id == order_data[0], client.orders))[0]
                    if order.status_id != 1:
                        window['PAY_ORDER'].update(disabled=True)
                    else:
                        window['PAY_ORDER'].update(disabled=False)
                except:
                    window['PAY_ORDER'].update(disabled=False)
            case 'PAY_ORDER':
                order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                order = list(filter(lambda order: order.order_id == order_data[0], client.orders))[0]
                order.status_id = 2
                session.commit()
                window['ORDERS_TABLE'].update(values=get_order_values())
            case 'DELETE_ORDER':
                try:
                    order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                    order = list(filter(lambda order: order.order_id == order_data[0], client.orders))[0]
                    client.del_order(order)
                    window['ORDERS_TABLE'].update(values=get_order_values())
                except:
                    sg.popup('Выберите заказ!', title='Ошибка!')

    window.close()
    del window
    return reset


def courier_window(courier: Courier):
    session = object_session(courier)
    def update_courier_window(courier: Courier):
        texts = sg.Column([
            [sg.Text('Имя')],
            [sg.Text('Фамилия')],
            [sg.Text('Телефон')],
        ], element_justification='r')
        fields = sg.Column([
            [sg.Input(key='FIRSTNAME', default_text=courier.first_name, size=(20, 1))],
            [sg.Input(key='LASTNAME', default_text=courier.last_name, size=(20, 1))],
            [sg.Input(key='PHONE', default_text=courier.phone_number, size=(20, 1))],
        ], element_justification='l')
        layout = [
            [texts, fields],
            [sg.OK('OK'), sg.Stretch(), sg.Cancel('Отмена', key='EXIT')]
        ]
        window = sg.Window('Редактирование', layout, element_justification='c', modal=True)
        while True:
            event, values = window.read(timeout=100)
            match event:
                case sg.WIN_CLOSED | 'EXIT':
                    session.rollback()
                    session.commit()
                    break
                case 'OK':
                    err_msg = ''
                    if not re.match(r'^[+]?[(]?\d{3}[)]?[-\s\.]?\d{3}[-\s\.]?\d{4,6}$',  # regex for phones
                                    values['PHONE']):
                        err_msg += "Неверный формат номера!\n"
                    if err_msg:
                        sg.popup(err_msg)
                    else:
                        try:
                            session = object_session(courier)
                            courier.first_name = values['FIRSTNAME'].capitalize()
                            courier.last_name = values['LASTNAME'].capitalize()
                            courier.phone_number = values['PHONE']
                            session.commit()
                            break
                        except:
                            print(traceback.format_exc())
                            sg.popup('Неверно введены данные', title='Ошибка!')
        window.close()
    get_order_values = lambda: [[o.order_id, o.client.first_name + ' ' + o.client.last_name,
                             o.client.phone_number, o.client.address, o.status.status_name] for o in courier.orders]
    l_col = sg.Column([
        [sg.Table(values=get_order_values(), headings=['ID', 'Клиент', 'Телефон', 'Адрес', 'Статус'],
                  auto_size_columns=False, enable_events=True,
                  col_widths=[3, 15, 8, 20, 8], key='ORDERS_TABLE')]
    ])
    r_col = sg.Column([
        [sg.Button('Показать выбранный', key='SHOW_ORDER')],
        [sg.Button('Заказ доставлен', key='DELIVER_ORDER')],
    ], element_justification='c')
    layout = [
        [sg.Frame(f'Курьер [ ID: {courier.courier_id} ]', [
            [sg.Text(f'{courier.first_name} {courier.last_name},'),
             sg.Text(f'Тел.:{courier.phone_number}', key='PHONE'),
             sg.Text(f'магазин: "{courier.shop.shop_name}"'), sg.Stretch(),
             sg.Button('Изм. данные', key='CHANGE_DATA')],
            [sg.HorizontalSeparator(pad=(0, 10))],
            [sg.Text('Заказы', font='14'), sg.Stretch()],
            [l_col, sg.VerticalSeparator(), r_col],
            [sg.HorizontalSeparator()],
            [sg.Exit('Выход', key='EXIT'), sg.Stretch()]
        ], element_justification='c', font='bold')]
    ]
    window = sg.Window(f'Курьер {courier.first_name} {courier.last_name}', layout, element_justification='c',
                       modal=True, finalize=True)
    reset = False
    while True:
        event, values = window.read(timeout=100)
        match event:
            case 'EXIT' | sg.WIN_CLOSED:
                reset = False
                session.commit()
                break
            case 'CHANGE_DATA':
                update_courier_window(courier)
                reset = True
                break
            case 'SHOW_ORDER':
                order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                order = list(filter(lambda order: order.order_id == order_data[0], courier.orders))[0]
                try:
                    order_window(order, courier=courier)
                    window['ORDERS_TABLE'].update(values=get_order_values())
                except:
                    print(traceback.format_exc())
            case 'ORDERS_TABLE':
                try:
                    order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                    order = list(filter(lambda order: order.order_id == order_data[0], courier.orders))[0]
                    if order.status_id != 4:
                        window['DELIVER_ORDER'].update(disabled=True)
                    else:
                        window['DELIVER_ORDER'].update(disabled=False)
                except:
                    window['DELIVER_ORDER'].update(disabled=False)
            case 'DELIVER_ORDER':
                order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                order = list(filter(lambda order: order.order_id == order_data[0], courier.orders))[0]
                order.status_id = 5
                session.commit()
                window['ORDERS_TABLE'].update(values=get_order_values())
    window.close()
    del window
    return reset


def order_window(order: Order, client: Client = None, shop: Shop = None, courier: Courier = None, show=False):

    session = object_session(order)
    def get_prod_values():
        return sorted([[op.product_id, op.product.product_name, op.product.price, op.quantity]
                       for op in order.products], key=lambda x: x[0])
    l_col = sg.Column([
        [sg.Text('Товары', font='14'), sg.Stretch()],
        [sg.Table(values=get_prod_values(), headings=['ID', 'Название', 'Цена, ₽', 'Кол-во'], auto_size_columns=False,
                  col_widths=[3, 23, 6, 5], key='PRODUCTS_TABLE')],
        [sg.Stretch(), sg.Text('Итого:', font='Arial 12 bold'), sg.Text(f'{order.price} ₽', font='Arial 12 bold', key='PRICE')]
    ], element_justification='c')
    r_col = sg.Column([
        [sg.Button('Добавить товар', key='ADD_PRODUCT', disabled=bool(courier))],
        [sg.Button('Удалить товар', key='REMOVE_PRODUCT', disabled=bool(courier))],
    ], element_justification='c')
    if (bool(shop) or bool(client)) and not show:
        cols = [sg.Stretch(), l_col, sg.VerticalSeparator(), r_col, sg.Stretch()]
    else:
        cols = [sg.Stretch(), l_col, sg.Stretch()]

    statuses = dict(session.query(Status.status_id, Status.status_name).all())
    if client and not show:
        shops = list(client.district.shop_names)
        exit = [sg.OK(), sg.Stretch(), sg.Exit('Отмена', key='EXIT')]
    else:
        exit = [sg.OK(), sg.Stretch()]
        shops = order.shop.shop_name
    if bool(client) or bool(courier):
        check = sg.Text(f'{order.courier.first_name} {order.courier.last_name}, '
                        f'Тел.:{order.courier.phone_number}' if order.courier else 'Не назначен')

    if shop:
        couriers_names = shop.get_courier_names()
        check = sg.Combo(couriers_names,
                         default_value=order.courier.get_name_phone() if order.courier else None,
                         key='COURIER')
    layout = [
        [sg.Frame(f'Заказ [ {order.order_id} ] от {order.purchase_date.strftime("%d.%m.%y %H:%M")}', [
            [sg.Text(f'Покупатель {order.client.first_name} {order.client.last_name}, '
                     f'Тел.:{order.client.phone_number}, Адрес: {order.client.address}')],
            [sg.Text(f'Магазин:'), sg.Combo(values=shops, default_value=None if client and not show else order.shop.shop_name,
                                            key='SHOP', size=(20, 1), enable_events=True, disabled=not bool(client) or show)],
            [sg.Text(f'Курьер:'), check],
            [sg.Text('Статус'), sg.OptionMenu(list(statuses.values()), default_value=statuses[order.status_id],
                                              key='STATUS', disabled=bool(client))],
            [sg.HorizontalSeparator(pad=(0, 10))],
            cols,
            [sg.HorizontalSeparator()],
            exit
        ], font='bold')]
    ]
    window = sg.Window(f'Заказ [ {order.order_id} ] от {order.purchase_date.strftime("%d.%m.%y %H:%M")}',
                       layout, element_justification='c', modal=True)

    def add_product_window(shop: Shop):
        products = dict(list(zip(shop.product_names, shop.products)))
        layout = [
            [sg.Text('Товар'), sg.Combo(values=list(products.keys()), size=(20, 1), enable_events=True, key='PRODUCT'),
             sg.Text('Кол-во:'), sg.Spin(values=[], initial_value=1, size=(2, 1), key='QUANTITY')],
            [sg.Button('Добавить', key='ADD'), sg.Stretch(), sg.Button('Отмена', key='EXIT')],
        ]
        window = sg.Window('Добавление товара', layout,
                           element_justification='c', modal=True)
        res = []
        while True:
            event, values = window.read(timeout=100)
            match event:
                case sg.WIN_CLOSED | 'EXIT':
                    res = 'closed'
                    break
                case 'PRODUCT':
                    window['QUANTITY'].update(values=list(range(products[values['PRODUCT']].quantity)))
                case 'ADD':
                    try:
                        res = products[values['PRODUCT']], int(values['QUANTITY'])
                        if not res[0]: res = []; raise Exception
                    except:
                        print(traceback.format_exc())
                        sg.popup('Неверно введены данные', title='Ошибка!')
                    break
        window.close()
        del window
        return res

    while True:
        event, values = window.read(timeout=100)
        match event:
            case sg.WIN_CLOSED | 'EXIT':
                session.rollback()
                session.commit()
                break
            case 'SHOP':
                for product in order.products:
                    order = session.merge(order)
                    product = session.merge(product)
                    order.remove_product(product.product)
                window['PRODUCTS_TABLE'].update(values=get_prod_values())
                window['PRICE'].update(f'{order.price} ₽')
            case 'OK':
                if show:
                    break
                elif client:
                    try:
                        if order.products:
                            order.shop = session.query(Shop).filter(Shop.shop_name == values['SHOP']).one()
                            session.commit()
                            break
                        else:
                            sg.popup('Список товаров не может быть пустым!', title='Ошибка!')
                    except:
                        print(traceback.format_exc())
                        if product_quantity_list == 'closed':
                            pass
                        sg.popup('Введите корректное название магазина!', title='Ошибка!')
                elif courier:
                    order.status = session.query(Status).filter(Status.status_name == values['STATUS']).one()
                    session.commit()
                    break
                elif shop:
                    order.status = session.query(Status).filter(Status.status_name == values['STATUS']).one()
                    order.courier = shop.couriers[couriers_names.index(values['COURIER'])]
                    session.commit()
                    break
            case 'ADD_PRODUCT':
                try:
                    product_quantity_list = []
                    if not values['SHOP']:
                        raise Exception
                    shop = session.query(Shop).filter(Shop.shop_name == values['SHOP']).one()
                    product_quantity_list = add_product_window(shop)
                    order.add_product(product_quantity_list[0], product_quantity_list[1])
                    order = session.merge(order)
                except:
                    print(traceback.format_exc())
                    if product_quantity_list != 'closed':
                        sg.popup('Введите корректное название магазина!', title='Ошибка!')
                window['PRODUCTS_TABLE'].update(values=get_prod_values())
                window['PRICE'].update(f'{order.price} ₽')
            case 'REMOVE_PRODUCT':
                try:
                    table_values = get_prod_values()
                    product = table_values[values['PRODUCTS_TABLE'][0]]
                    product = session.query(Product).filter(Product.product_id == product[0]).one()
                    order = session.merge(order)
                    product = session.merge(product)
                    order.remove_product(product)
                except:
                    print(traceback.format_exc())
                    sg.popup('Выберите товар!', title='Ошибка!')
                window['PRODUCTS_TABLE'].update(values=get_prod_values())
                window['PRICE'].update(f'{order.price} ₽')
    window.close()
    del window


def shop_window(shop: Shop):
    def add_or_edit_prod(name='', price='', quantity=''):
        texts = sg.Column([
            [sg.Text('Название')],
            [sg.Text('Цена')],
            [sg.Text('Количество')],
        ], element_justification='r')
        fields = sg.Column([
            [sg.Input(default_text=name, key='NAME', size=(20, 1))],
            [sg.Input(default_text=price, key='PRICE', size=(20, 1))],
            [sg.Input(default_text=quantity, key='QUANTITY', size=(20, 1))]
        ], element_justification='l')
        layout = [
            [texts, fields],
            [sg.Button('Добавить' if not name else 'ОК', key='ADD')],
        ]
        window = sg.Window('Добавление товара' if not name else 'Редактирование товара', layout,
                           element_justification='c', modal=True)
        res = []
        while True:
            event, values = window.read(timeout=100)
            match event:
                case sg.WIN_CLOSED:
                    res = 'closed'
                    break
                case 'ADD':
                    try:
                        res = values['NAME'], Decimal(values['PRICE']), int(values['QUANTITY'])
                        if not res[0]: res = []; raise Exception
                    except:
                        print(traceback.format_exc())
                        sg.popup('Неверно введены данные', title='Ошибка!')
                    finally:
                        break
        window.close()
        del window
        return res

    def get_prod_values():
        return sorted([[p.product_id, p.product_name, p.quantity, p.price] for p in shop.products], key=lambda x: x[0])
    l_col = sg.Column([
        [sg.Text('Товары', font='14'), sg.Stretch()],
        [sg.Button('+', key='ADD_PRODUCT'), sg.Button('-', key='DEL_PRODUCT'), sg.Button('...', key='EDIT_PRODUCT')],
        [sg.Table(values=get_prod_values(), headings=['ID', 'Название', 'Кол-во', 'Цена, ₽'], auto_size_columns=False,
                  col_widths=[3, 20, 6, 7], key='PRODUCTS_TABLE')]
    ], element_justification='c')

    def get_order_values():
        return sorted([[o.order_id, o.client_id, o.purchase_date.isoformat(' ')[:16], o.courier_id, o.price, o.status.status_name]
                       for o in shop.orders], key=lambda x: x[0])
    r_col = sg.Column([
        [sg.Text('Заказы', font='14'), sg.Stretch()],
        [sg.Button('Показать выбранный', key='EDIT_ORDER')],
        [sg.Table(values=get_order_values(), headings=['ID', 'Клиент', 'Дата', 'Курьер', 'Сумма, ₽', 'Статус'],
                  auto_size_columns=False,
                  col_widths=[3, 5, 12, 6, 7, 7], key='ORDERS_TABLE')]
    ], element_justification='c')
    filtered = False
    layout = [
        [sg.Frame(f'Магазин [ ID: {shop.shop_id} ]: "{shop.shop_name}"', [
            [sg.Button('Районы', key='DISTRICTS'),
             sg.Button('Курьеры', key='COURIERS')],
            [sg.HorizontalSeparator(pad=(0, 10))],
            [l_col, sg.VerticalSeparator(), r_col],
            [sg.HorizontalSeparator()],
            [sg.Text('ID клиента'), sg.Input(key='CLIENT_ID', size=(3, 1)), sg.Button('Поиск', key='USER_FILTER')],
            [sg.Text('ID курьера'), sg.Input(key='COURIER_ID', size=(3, 1)), sg.Button('Поиск', key='COURIER_FILTER')],
            [sg.Button('Сброс (показать все)', key='TABLE_RESET')],
            [sg.HorizontalSeparator()],
            [sg.Exit('Выход', key='EXIT'), sg.Stretch()]
        ], element_justification='c', font='bold')]
    ]
    window = sg.Window(f'Магазин "{shop.shop_name}"', layout, element_justification='c', modal=True, finalize=True)
    session = object_session(shop)
    while True:
        event, values = window.read(timeout=100)
        match event:
            case 'EXIT' | sg.WIN_CLOSED:
                session.commit()
                break
            case 'ADD_PRODUCT':
                if filtered:
                    sg.popup('Значения будут сброшены', title='Сброс')
                    filtered=False
                try:
                    product = add_or_edit_prod()
                    product = Product(product[0], product[1], product[2], shop)
                    session.add(product)
                    session.commit()
                except:
                    print(traceback.format_exc())
                    if product == 'closed':
                        pass
                window['PRODUCTS_TABLE'].update(values=get_prod_values())
            case 'DEL_PRODUCT':
                if filtered:
                    sg.popup('Значения будут сброшены', title='Сброс')
                    filtered=False
                try:
                    table_values = get_prod_values()
                    product = table_values[values['PRODUCTS_TABLE'][0]]
                    product = session.query(Product).filter(Product.product_id == product[0]).one()
                    shop.del_product(product)
                    session.delete(product)
                    session.commit()
                except:
                    print(traceback.format_exc())
                    sg.popup('Выберите товар!', title='Ошибка!')
                window['PRODUCTS_TABLE'].update(values=get_prod_values())
            case 'EDIT_PRODUCT':
                if filtered:
                    sg.popup('Значения будут сброшены', title='Сброс')
                    filtered=False
                try:
                    table_values = get_prod_values()
                    id = table_values[values['PRODUCTS_TABLE'][0]][0]
                    product = table_values[values['PRODUCTS_TABLE'][0]][1:4]
                    product_data = add_or_edit_prod(product[0], product[2], product[1])
                    print(product_data)
                    product = session.query(Product).filter(Product.product_id == id).one()
                    product.product_name = product_data[0]
                    product.price = product_data[1]
                    product.quantity = product_data[2]
                    session.commit()
                except:
                    print(traceback.format_exc())
                    sg.popup('Выберите товар!', title='Ошибка!')
                window['PRODUCTS_TABLE'].update(values=get_prod_values())
            case 'EDIT_ORDER':
                order_data = get_order_values()[values['ORDERS_TABLE'][0]]
                order = list(filter(lambda order: order.order_id == order_data[0], shop.orders))[0]
                try:
                    order_window(order, shop=shop)
                    window['ORDERS_TABLE'].update(values=get_order_values())
                except:
                    print(traceback.format_exc())
            case 'DISTRICTS':
                pass
            case 'COURIERS':
                pass
            case 'USER_FILTER':
                pass
            case 'COURIER_FILTER':
                pass
            case 'TABLE_RESET':
                window['PRODUCTS_TABLE'].update(values=get_prod_values())
                window['ORDERS_TABLE'].update(values=get_order_values())

    window.close()


def client_reg():
    with Session() as session:
        districts = list(zip(*session.query(District.district_name).all()))[0]
    texts = sg.Column([
        [sg.Text('Имя')],
        [sg.Text('Фамилия')],
        [sg.Text('Телефон')],
        [sg.Text('Район')],
        [sg.Text('Адрес')],
        [],
    ], element_justification='r')
    fields = sg.Column([
        [sg.Input(key='FIRSTNAME', size=(20, 1))],
        [sg.Input(key='LASTNAME', size=(20, 1))],
        [sg.Input(key='PHONE', size=(20, 1))],
        [sg.Combo(values=districts, key='DISTRICT', size=(20, 1))],
        [sg.Multiline(key='ADDRESS', no_scrollbar=True, size=(20, 2))],
    ], element_justification='l')
    layout = [
        [texts, fields],
        [sg.Button('Зарегистрировать', key='bREG')],
        [sg.OK('OK'), sg.Stretch()]
    ]
    window = sg.Window('Регистрация покупателя', layout, element_justification='c', modal=True)

    while True:
        event, values = window.read(timeout=100)
        match event:
            case 'OK' | sg.WIN_CLOSED:
                session.commit()
                break
            case 'bREG':
                err_msg = ''
                if not re.match(r'^[+]?[(]?\d{3}[)]?[-\s\.]?\d{3}[-\s\.]?\d{4,6}$',  # regex for phones
                                values['PHONE']):
                    err_msg += "Неверный формат номера!\n"
                if err_msg:
                    sg.popup(err_msg)
                else:
                    try:
                        with Session() as session:
                            district = session.query(District). \
                                filter(District.district_name == values['DISTRICT']).one()
                            client = Client(values['FIRSTNAME'].capitalize(),
                                            values['LASTNAME'].capitalize(),
                                            values['PHONE'],
                                            values['ADDRESS'],
                                            district)
                            session.add(client)
                            session.commit()
                            sg.popup(f'Покупатель успешно зарегистрирован!', f'id для входа: {client.client_id}',
                                     title='Успех!')
                    except:
                        sg.popup('Неверно введены данные', title='Ошибка!')
    window.close()
    del window


def courier_reg():
    texts = sg.Column([
        [sg.Text('Имя')],
        [sg.Text('Фамилия')],
        [sg.Text('Телефон')],
        [sg.Text('ID магазина')],
    ], element_justification='r')
    fields = sg.Column([
        [sg.Input(key='FIRSTNAME', size=(20, 1))],
        [sg.Input(key='LASTNAME', size=(20, 1))],
        [sg.Input(key='PHONE', size=(20, 1))],
        [sg.Input(key='SHOP_ID', size=(3, 1))],
    ], element_justification='l')
    layout = [
        [texts, fields],
        [sg.Button('Зарегистрировать', key='bREG')],
        [sg.OK('OK'), sg.Stretch()]
    ]
    window = sg.Window('Регистрация курьера', layout, element_justification='c', modal=True)
    while True:
        event, values = window.read(timeout=100)
        match event:
            case 'OK' | sg.WIN_CLOSED:
                break
            case 'bREG':
                err_msg = ''
                if not re.match(r'^[+]?[(]?\d{3}[)]?[-\s\.]?\d{3}[-\s\.]?\d{4,6}$',  # regex for phones
                                values['PHONE']):
                    err_msg += "Неверный формат номера!\n"
                if err_msg:
                    sg.popup(err_msg)
                else:
                    try:
                        with Session() as session:
                            courier = Courier(values['FIRSTNAME'].capitalize(),
                                              values['LASTNAME'].capitalize(),
                                              values['PHONE'],
                                              int(values['SHOP_ID']))
                            session.add(courier)
                            session.commit()
                            sg.popup(f'Курьер успешно зарегистрирован!', f'id для входа: {courier.courier_id}',
                                     title='Успех!')
                    except Exception:
                        sg.popup('Неверно введены данные', title='Ошибка!')
    window.close()
    del window


def shop_reg():
    with Session() as session:
        districts = list(zip(*session.query(District.district_name).all()))[0]
    layout = [
        [sg.Text('Название'), sg.Input(key='NAME', size=(20, 1))],
        [sg.Text('Выберите районы, в которых вы работаете:')],
        [
            sg.Listbox(districts, size=(20, 20), enable_events=True,
                       select_mode='multiple', key='SELECTED_DISTRICTS'),
            sg.Button('->', disabled=True),
            sg.Listbox(values=[], size=(20, 10), key='DISTRICTS')
        ],
        [sg.Button('Зарегистрировать', key='bREG')],
        [sg.OK('OK'), sg.Stretch()]
    ]
    window = sg.Window('Регистрация магазина', layout, element_justification='c', modal=True)
    while True:
        event, values = window.read(timeout=10)
        match event:
            case 'OK' | sg.WIN_CLOSED:
                break
            case 'SELECTED_DISTRICTS':
                window['DISTRICTS'].update(values['SELECTED_DISTRICTS'])
            case 'bREG':
                try:
                    with Session() as session:
                        shop = Shop(values['NAME'].capitalize())
                        shop_districts = session.query(District). \
                            filter(District.district_name.in_(values['SELECTED_DISTRICTS'])).all()
                        if values['SELECTED_DISTRICTS'] and values['NAME']:
                            for district in shop_districts:
                                shop.add_district(district)
                            session.add(shop)
                            session.commit()
                            sg.popup(f'Магазин успешно зарегистрирован!', f'id для входа: {shop.shop_id}',
                                     title='Успех!')
                        else:
                            raise Exception
                except:
                    sg.popup('Неверно введены данные', title='Ошибка!')
    window.close()
    del window


def main():
    layout = [
        [sg.Frame('Покупатель', [
            [sg.Text('Введите id'), sg.Input(key='CLIENT_ID')],
            [sg.Button('Вход', key='bCLIENT_LOGIN'), sg.Button('Регистрация', key='bCLIENT_REG')]],
                  font='bold', element_justification='center')],
        [sg.Frame('Курьер', [
            [sg.Text('Введите id'), sg.Input(key='COURIER_ID')],
            [sg.Button('Вход', key='bCOURIER_LOGIN'), sg.Button('Регистрация', key='bCOURIER_REG')]],
                  font='bold', element_justification='center')],
        [sg.Frame('Магазин', [
            [sg.Text('Введите id'), sg.Input(key='SHOP_ID')],
            [sg.Button('Вход', key='bSHOP_LOGIN'), sg.Button('Регистрация', key='bSHOP_REG')]],
                  font='bold', element_justification='center')],
        [sg.Exit('Выход', k='EXIT')]
    ]
    window = sg.Window('Вход', layout, element_justification='c', size=(200, 300), finalize=True)
    session = Session()
    while True:
        log_err = lambda: sg.popup('Ошибка! Попробуйте зарегистрироваться', title='ОШИБКА!')
        event, values = window.read(timeout=100)
        match event:
            case 'EXIT' | sg.WIN_CLOSED:
                break
            case 'bCLIENT_LOGIN':
                try:
                    user = session.query(Client). \
                        filter(Client.client_id == int(values['CLIENT_ID'])).one()
                    # window.close()
                    res = True
                    while res:
                        res = client_window(user)
                except:
                    print(traceback.format_exc())
                    log_err()
            case 'bCOURIER_LOGIN':
                try:
                    user = session.query(Courier). \
                        filter(Courier.courier_id == int(values['COURIER_ID'])).one()
                    # window.close()
                    res = True
                    while res:
                        res = courier_window(user)
                except:
                    print(traceback.format_exc())
                    log_err()
            case 'bSHOP_LOGIN':
                try:
                    user = session.query(Shop). \
                        filter(Shop.shop_id == int(values['SHOP_ID'])).one()
                    # window.close()
                    shop_window(user)
                except:
                    log_err()
            case 'bCLIENT_REG':
                client_reg()
            case 'bCOURIER_REG':
                courier_reg()
            case 'bSHOP_REG':
                shop_reg()
    session.close()
    window.close()


if __name__ == '__main__':
    main()
