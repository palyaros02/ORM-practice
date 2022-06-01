CREATE TABLE districts (
	id 				SERIAL 		PRIMARY KEY,
	district_name  	VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE shops (
	id 			SERIAL 		PRIMARY KEY,
	shop_name  	VARCHAR(30) NOT NULL
);

CREATE TABLE couriers (
	id 			 SERIAL 	 PRIMARY KEY,
	shop_id 	 INT 		 REFERENCES shops(id),
	first_name 	 VARCHAR(20) NOT NULL,
	last_name 	 VARCHAR(30) NOT NULL,
	phone_number CHAR(12) 	 NOT NULL
);

CREATE TABLE products (
	id 			 SERIAL	PRIMARY KEY,
	shop_id 	 INT 	REFERENCES shops(id),
	product_name TEXT 	NOT NULL,
	price 		 MONEY 	NOT NULL,
	quantity 	 INT
);

CREATE TABLE shops_districts (
	shop_id 		INT REFERENCES shops(id),
	district_id 	INT REFERENCES districts(id),
	time_to_deliver INT NOT NULL,
	
	PRIMARY KEY (shop_id, district_id)
);

CREATE TABLE clients (
	id 			 SERIAL 	 PRIMARY KEY,
	first_name 	 VARCHAR(20) NOT NULL,
	last_name 	 VARCHAR(30) NOT NULL,
	phone_number CHAR(12)	 NOT NULL,
	district_id  INT 		 REFERENCES districts(id),
	address 	 TEXT 		 NOT NULL
);

CREATE TABLE statuses (
	id 			INT 		PRIMARY KEY,
	status  	VARCHAR(20) NOT NULL
);

CREATE TABLE orders (
	id 			 	SERIAL 	PRIMARY KEY,
	client_id 		INT 	REFERENCES clients(id),
	shop_id 		INT 	REFERENCES shops(id),
	purchase_date 	TIMESTAMP,
	status_id 		INT 	REFERENCES statuses(id),
	courier_id  	INT 	REFERENCES couriers(id)
);	

CREATE TABLE orders_products (
	order_id 	INT REFERENCES orders(id),
	product_id 	INT REFERENCES products(id),
	quantity 	INT NOT NULL,
	
	PRIMARY KEY (order_id , product_id)
);
