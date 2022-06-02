from decimal import Decimal
from typing import Union

import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from datetime import datetime, time

from config import Base
from orm.extensions import Extension


class Shop(Base, Extension):
    __tablename__  = 'shops'
    __table_args__ = {'comment': 'Магазины'}

    shop_id   = sa.Column(sa.Integer,    primary_key=True, autoincrement=True)
    shop_name = sa.Column(sa.String(50), nullable=False)

    # relations
    shop_districts: list['ShopDistrict'] = \
        sa.orm.relationship('ShopDistrict', back_populates='shop', cascade='all, delete')
    orders: list['Order'] = \
        sa.orm.relationship('Order', back_populates='shop', cascade='all, delete')
    couriers: list['Courier'] = \
        sa.orm.relationship('Courier', back_populates='shop', cascade='all, delete')
    products: list['Product'] = \
        sa.orm.relationship('Product', back_populates='shop', cascade='all, delete')

    # proxies
    districts: list['District'] = \
        association_proxy(target_collection='shop_districts', attr='district')
    district_names: list[str] = \
        association_proxy(target_collection='shop_districts', attr='district_name')

    def __init__(self, name: str):
        self.shop_name = name

    def __repr__(self):
        return self._repr(shop_id=self.shop_id,
                          shop_name=self.shop_name)

    def add_district(self, district: Union[int, 'District'], delivery_time: time):
        self.shop_districts.append(
            ShopDistrict(shop=self, district=district, delivery_time=delivery_time)
        )

    def add_courier(self, courier: 'Courier'):
        self.couriers.append(courier)
        courier.shop = self

    def add_product(self, product: 'Product'):
        self.products.append(product)
        product.shop = self


class District(Base, Extension):
    __tablename__  = 'districts'
    __table_args__ = {'comment': 'Районы доставки'}

    district_id   = sa.Column(sa.Integer,    primary_key=True, autoincrement=True)
    district_name = sa.Column(sa.String(30), nullable=False, unique=True)

    # relations
    shop_districts: list['ShopDistrict'] = \
        sa.orm.relationship('ShopDistrict', back_populates='district', cascade='all, delete')

    # proxies
    shops: list[Shop] = \
        association_proxy(target_collection='shop_districts', attr='shop')
    shop_names: list[str] = \
        association_proxy(target_collection='shop_districts', attr='shop_name')

    def __init__(self, name: str):
        self.district_name = name

    def __repr__(self):
        return self._repr(district_id=self.district_id,
                          district_name=self.district_name)


class ShopDistrict(Base, Extension):
    __tablename__  = 'shops_districts'
    __table_args__ = {'comment': 'Вспомогательная таблица для связи '
                                 'магазинов и районов доставки'}

    shop_id     = sa.Column(sa.Integer, sa.ForeignKey('shops.shop_id', ondelete="CASCADE"),
                                        primary_key=True)
    district_id = sa.Column(sa.Integer, sa.ForeignKey('districts.district_id', ondelete="CASCADE"),
                                        primary_key=True)

    delivery_time = sa.Column(sa.Time, nullable=False)

    # relations
    shop: 'Shop' = \
        sa.orm.relationship('Shop', cascade='save-update')
    district: 'District' = \
        sa.orm.relationship('District', cascade='save-update')

    # proxies
    shop_name: str = \
        association_proxy(target_collection='shop', attr='shop_name')
    district_name: str = \
        association_proxy(target_collection='district', attr='district_name')

    def __init__(self, shop: Shop = None, district: District = None, delivery_time: time = None):
        self.shop = shop
        self.district = district
        self.delivery_time = delivery_time
    # def __init__(self, shop: Union['Shop', int] = None, district: Union['District', int] = None,
    #              delivery_time: time = None):
    #     try:
    #         self.set_id_or_link(shop, Shop)
    #         self.set_id_or_link(district, District)
    #         self.delivery_time = delivery_time
    #     except IntegrityError:
    #         pass
    #     except InvalidRequestError as e:
    #         print(e)

    def __repr__(self):
        return self._repr(shop_id=self.shop_id,
                          district_id=self.district_id,
                          delivery_time=self.delivery_time)


class Courier(Base, Extension):
    __tablename__  = 'couriers'
    __table_args__ = {'comment': 'Курьеры'}

    courier_id   = sa.Column(sa.Integer,    primary_key=True, autoincrement=True)
    shop_id      = sa.Column(sa.Integer,    sa.ForeignKey('shops.shop_id', ondelete="CASCADE"), nullable=False)
    first_name   = sa.Column(sa.String(20), nullable=False)
    last_name    = sa.Column(sa.String(30), nullable=False)
    phone_number = sa.Column(sa.String(12), nullable=False)

    # relations
    orders: list['Order'] = \
        sa.orm.relationship('Order', back_populates='courier', cascade='all, delete')
    shop: 'Shop' = \
        sa.orm.relationship('Shop', back_populates='couriers')

    def __repr__(self):
        return self._repr(courier_id=self.courier_id,
                          shop_id=self.shop_id,
                          first_name=self.first_name,
                          last_name=self.last_name,
                          phone_number=self.phone_number)

    def __init__(self, first_name: str, last_name: str, phone: str, shop: Union[int, Shop] = None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone
        self.set_id_or_link(shop, Shop)

    def set_shop(self, shop: Union[int, Shop]):
        self.set_id_or_link(shop, Shop)


class Client(Base, Extension):
    __tablename__  = 'clients'
    __table_args__ = {'comment': 'Покупатели'}

    client_id    = sa.Column(sa.Integer,    primary_key=True, autoincrement=True)
    first_name   = sa.Column(sa.String(20), nullable=False)
    last_name    = sa.Column(sa.String(30), nullable=False)
    phone_number = sa.Column(sa.String(12), nullable=False)
    district_id  = sa.Column(sa.Integer,    sa.ForeignKey('districts.district_id'), nullable=False)
    address      = sa.Column(sa.Text,       nullable=False)

    # relations
    district: District \
        = sa.orm.relationship('District')
    orders: list['Order'] \
        = sa.orm.relationship('Order', back_populates='client', cascade='all, delete')

    def __repr__(self):
        return self._repr(client_id=self.client_id,
                          first_name=self.first_name,
                          last_name=self.last_name,
                          phone_number=self.phone_number,
                          district_id=self.district_id,
                          address=self.address)

    def __init__(self, first_name: str, last_name: str, phone: str, address: str,
                 district: Union[int, District] = None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone
        self.address = address
        self.set_id_or_link(district, District)

    def set_district(self, district: Union[int, District] = None):
        self.set_id_or_link(district, District)

    def add_order(self, order: 'Order', date: datetime = datetime.now()):
        self.orders.append(order)
        order.client = self
        order.purchase_date = date


class Status(Base, Extension):
    __tablename__  = 'statuses'
    __table_args__ = {'comment': 'Статусы заказов'}

    status_id = sa.Column(sa.Integer,    primary_key=True)
    status_name    = sa.Column(sa.String(18), nullable=False, unique=True)

    def __repr__(self):
        return self._repr(status_id=self.status_id,
                          status_name=self.status_name)

    def __init__(self, status_name: str):
        self.status_name = status_name


class Product(Base, Extension):
    __tablename__  = 'products'
    __table_args__ = {'comment': 'Товары'}

    product_id   = sa.Column(sa.Integer,        primary_key=True, autoincrement=True)
    shop_id      = sa.Column(sa.Integer,        sa.ForeignKey('shops.shop_id', ondelete="CASCADE"), nullable=False)
    product_name = sa.Column(sa.Text,           nullable=False)
    price        = sa.Column(sa.Numeric(10, 2), nullable=False)
    quantity     = sa.Column(sa.Integer)

    # relations
    orders: list['OrderProducts'] = \
        sa.orm.relationship('OrderProducts', back_populates='product', cascade='all, delete')
    shop: Shop = \
        sa.orm.relationship('Shop', back_populates='products')

    def __repr__(self):
        return self._repr(product_id=self.product_id,
                          shop_id=self.shop_id,
                          product_name=self.product_name,
                          price=self.price,
                          quantity=self.quantity)

    def __init__(self, name: str, price: float, quantity: int, shop: Union[Shop, int] = None):
        self.product_name = name
        self.price = price
        self.quantity = quantity
        self.set_id_or_link(shop, Shop)


class Order(Base, Extension):
    __tablename__  = 'orders'
    __table_args__ = {'comment': 'Заказы'}

    order_id      = sa.Column(sa.Integer,  primary_key=True, autoincrement=True)
    purchase_date = sa.Column(sa.DateTime, nullable=False)
    client_id     = sa.Column(sa.Integer,  sa.ForeignKey('clients.client_id', ondelete="CASCADE"), nullable=False)
    shop_id       = sa.Column(sa.Integer,  sa.ForeignKey('shops.shop_id', ondelete="CASCADE"), nullable=False)
    status_id     = sa.Column(sa.Integer,  sa.ForeignKey('statuses.status_id'), nullable=False, default=1)
    courier_id    = sa.Column(sa.Integer,  sa.ForeignKey('couriers.courier_id'))

    # relations
    client: Client = \
        sa.orm.relationship('Client', back_populates='orders')
    shop: Shop = \
        sa.orm.relationship('Shop', back_populates='orders')
    courier: Courier = \
        sa.orm.relationship('Courier', back_populates='orders')
    status: Status = \
        sa.orm.relationship('Status')
    products: list['OrderProducts'] \
        = sa.orm.relationship('OrderProducts', back_populates='order', cascade='all, delete')

    # proxies
    products_names: list[str] = \
        association_proxy('products', 'products_names')

    def __repr__(self):
        return self._repr(order_id=self.order_id,
                          client_id=self.client_id,
                          shop_id=self.shop_id,
                          purchase_date=self.purchase_date,
                          status_id=self.status_id,
                          courier_id=self.courier_id)

    def __init__(self, client: Union[Client, int] = None, shop: Union[Shop, int] = None,
                 courier: Union[Courier, int] = None, date: datetime = datetime.now()):
        self.set_id_or_link(client, Client)
        self.set_id_or_link(shop, Shop)
        self.set_id_or_link(courier, Courier)
        self.purchase_date = date

    def add_product(self, product: Product, quantity=1):
        if product.quantity <= quantity:
            quantity = product.quantity
        if product.product_name in self.products_names:
            self.products[self.products_names.index(product.product_name)].quantity += quantity
        else:
            self.products.append(OrderProducts(order=self, product=product, quantity=quantity))
        product.quantity -= quantity

    def remove_product(self, product: Product):
        order_product = sorted(product.orders, key=lambda obj: obj.product_id == product.product_id, reverse=True)[0]
        product.quantity += order_product.quantity
        self.products.remove(order_product)
        del order_product

    def set_status(self, status: Union[Status, int]):
        self.set_id_or_link(status, Status)

    def set_courier(self, courier: Union[Courier, int]):
        self.set_id_or_link(courier, Courier)

    @property
    def price(self) -> Decimal:
        products = []
        quantities = []
        for item in self.products:
            products.append(item.product)
            quantities.append(item.quantity)
        s = Decimal(0.00)
        for product, quantity in products, quantities:
            s += product.price * quantity
        return s


class OrderProducts(Base, Extension):
    __tablename__  = 'order_products'
    __table_args__ = {'comment': 'Вспомогательная таблица для связи '
                                 'заказа и товаров в этом заказе'}

    order_id   = sa.Column(sa.Integer, sa.ForeignKey('orders.order_id', ondelete='CASCADE'),
                                       primary_key=True, nullable=False)
    product_id = sa.Column(sa.Integer, sa.ForeignKey('products.product_id', ondelete='CASCADE'),
                                       primary_key=True, nullable=False)
    quantity  = sa.Column(sa.Integer,  nullable=False)

    # relations
    order: Order = \
        sa.orm.relationship('Order')
    product: Product = \
        sa.orm.relationship('Product')

    # proxies
    products_names: list[str] = \
        association_proxy('product', 'product_name')

    def __repr__(self):
        return self._repr(order_id=self.order_id,
                          product_id=self.product_id,
                          quantity=self.quantity)

    def __init__(self, order: Union[Order, int] = None, product: Union[Product, int] = None, quantity: int = None):
        self.set_id_or_link(order, Order)
        self.set_id_or_link(product, Product)
        self.quantity = quantity


class Log(Base, Extension):
    __tablename__  = 'logs'
    __table_args__ = {'comment': 'Журнал логгирования'}

    log_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    change_date = sa.Column(sa.DateTime, nullable=False)
    operation_type = sa.Column(sa.String(10), nullable=False)
    table_name = sa.Column(sa.String(20), nullable=False)

    def __repr__(self):
        return self._repr(id=self.log_id,
                          change_date=self.change_date,
                          operation_type=self.operation_type,
                          table_name=self.table_name)
