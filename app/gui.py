import PySimpleGUI as sg
import re
from sqlalchemy.exc import NoResultFound

from config import Base, engine, Session
from orm.tables import *


def client_window(client: Client):
    sg.popup(repr(client))


def courier_window(courier: Courier):
    sg.popup(repr(courier))


def shop_window(shop: Shop):
    sg.popup(shop.get_info())


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
                    except NoResultFound:
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
    window = sg.Window('Регистрация магазина', layout, element_justification='c', modal=True, finalize=True)
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
                        shop_districts = session.query(District).\
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
                  font='Bold', element_justification='center')],
        [sg.Frame('Курьер', [
            [sg.Text('Введите id'), sg.Input(key='COURIER_ID')],
            [sg.Button('Вход', key='bCOURIER_LOGIN'), sg.Button('Регистрация', key='bCOURIER_REG')]],
                  font='Bold', element_justification='center')],
        [sg.Frame('Магазин', [
            [sg.Text('Введите id'), sg.Input(key='SHOP_ID')],
            [sg.Button('Вход', key='bSHOP_LOGIN'), sg.Button('Регистрация', key='bSHOP_REG')]],
                  font='Bold', element_justification='center')],
        [sg.Exit('Выход', k='EXIT')]
    ]
    window = sg.Window('Вход', layout, element_justification='c', size=(200, 300), finalize=True)
    while True:
        log_err = lambda: sg.popup('Ошибка! Попробуйте зарегистрироваться', title='ОШИБКА!')
        event, values = window.read(timeout=100)
        match event:
            case 'EXIT' | sg.WIN_CLOSED:
                break
            case 'bCLIENT_LOGIN':
                with Session() as session:
                    try:
                        user = session.query(Client). \
                            filter(Client.client_id == int(values['CLIENT_ID'])).one()
                        client_window(user)
                    except NoResultFound:
                        log_err()
            case 'bCOURIER_LOGIN':
                with Session() as session:
                    try:
                        user = session.query(Courier). \
                            filter(Courier.courier_id == int(values['COURIER_ID'])).one()
                        courier_window(user)
                    except NoResultFound:
                        log_err()
            case 'bSHOP_LOGIN':
                with Session() as session:
                    try:
                        user = session.query(Shop). \
                            filter(Shop.shop_id == int(values['SHOP_ID'])).one()
                        shop_window(user)
                    except NoResultFound:
                        log_err()
            case 'bCLIENT_REG':
                client_reg()
            case 'bCOURIER_REG':
                courier_reg()
            case 'bSHOP_REG':
                shop_reg()
    window.close()


if __name__ == '__main__':
    main()
