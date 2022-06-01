CREATE TABLE logs (
	id 				SERIAL 		PRIMARY KEY,
	change_date 	TIMESTAMP 	NOT NULL,
	operation_type 	VARCHAR(10) NOT NULL,
	table_name 		VARCHAR(20) NOT NULL
);

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
	FOR EACH ROW EXECUTE FUNCTION log();

INSERT INTO shops(shop_name) VALUES ('Новый');

INSERT INTO districts(district_name) VALUES ('Войковский');

INSERT INTO clients (first_name, last_name, phone_number, district_id, address) VALUES
('Ярослав', 'Паламарчук', '88005553535', 12, '6 общага');

INSERT INTO products (shop_id, product_name, price, quantity) VALUES 
(4, 'Булка свежая', 15, 100);

INSERT INTO couriers (shop_id, first_name, last_name, phone_number) VALUES 
(4, 'Булочник', 'Булкин', '88005553536');

INSERT INTO orders (client_id, shop_id, purchase_date, status_id, courier_id) VALUES
(16, 4, CURRENT_TIMESTAMP, 1, 11);

UPDATE couriers SET first_name = 'Иван' WHERE first_name = 'Булочник';

DELETE FROM shops_districts WHERE district_id = (SELECT id FROM districts WHERE district_name = 'Басманный');
DELETE FROM clients  WHERE district_id = (SELECT id FROM districts WHERE district_name = 'Басманный');
DELETE FROM districts WHERE district_name = 'Басманный';

CREATE OR REPLACE FUNCTION clear_orders()
RETURNS TRIGGER AS $body$
BEGIN
	DELETE FROM orders_products WHERE order_id = OLD.id;     
   	RETURN OLD;
END;
$body$ LANGUAGE plpgsql;

CREATE TRIGGER clear_orders
	BEFORE DELETE ON orders
	FOR EACH ROW EXECUTE FUNCTION clear_orders();
	
CREATE OR REPLACE FUNCTION clear_client_orders()
RETURNS TRIGGER AS $body$
BEGIN
	DELETE FROM orders WHERE client_id = OLD.id;     
   	RETURN OLD;
END;
$body$ LANGUAGE plpgsql;

CREATE TRIGGER clear_client_orders
	BEFORE DELETE ON clients
	FOR EACH ROW EXECUTE FUNCTION clear_client_orders();	

DELETE FROM clients WHERE first_name = 'Ярослав';