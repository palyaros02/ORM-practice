insert into districts(district_name) values
('Академический'),
('Алексеевский'),
('Алтуфьевский'),
('Арбат'),
('Аэропорт'),
('Бабушкинский'),
('Басманный'),
('Беговой'),
('Бескудниковский'),
('Бибирево'),
('Бирюлёво Восточное');

insert into shops(shop_name) values
('Рога и Копыта'),
('Эльдорадо'),
('У Петровича');

insert into shops_districts (shop_id, district_id, time_to_deliver) values
(1, 1, 72),
(1, 2, 48),
(1, 3, 24),
(2, 4, 12),
(2, 5, 96),
(2, 6, 20),
(3, 7, 70),
(3, 8, 15),
(3, 9, 20),
(3, 1, 72);

insert into couriers (shop_id, first_name, last_name, phone_number) values 
(2, 'Pauly', 'Higgen', '4075096814'),
(1, 'Dre', 'Finnes', '9994922979'),
(2, 'Denis', 'Portis', '5715044617'),
(1, 'Georges', 'Iannetti', '1184784718'),
(2, 'Annemarie', 'Topham', '7585643810'),
(1, 'Berkie', 'Benka', '5753291204'),
(1, 'Baily', 'Doole', '6347544174'),
(2, 'Cleavland', 'Cronshaw', '5403015835'),
(1, 'Rowe', 'Schultze', '5612134981'),
(1, 'Neda', 'Shefton', '8087398014');

insert into products (shop_id, product_name, price, quantity) values 
(2, 'Appetizer - Smoked Salmon / Dill', 290.83, 69),
(1, 'Clams - Bay', 693.39, 20),
(1, 'Mushrooms - Honey', 195.44, 39),
(3, 'Yogurt - Cherry, 175 Gr', 83.34, 17),
(1, 'Venison - Liver', 988.93, 20),
(1, 'Wine - Barolo Fontanafredda', 450.78, 11),
(1, 'Wine - Red, Gamay Noir', 792.18, 48),
(3, 'Soup Campbells', 538.72, 52),
(2, 'Amarula Cream', 31.13, 82),
(2, 'Lychee', 819.37, 95),
(2, 'Schnappes Peppermint - Walker', 962.96, 24),
(1, 'Shrimp - 21/25, Peel And Deviened', 39.62, 92),
(1, 'Fib N9 - Prague Powder', 261.2, 57),
(2, 'Puree - Kiwi', 650.04, 43),
(3, 'Filling - Mince Meat', 649.02, 19),
(1, 'Chip - Potato Dill Pickle', 485.11, 37),
(2, 'Spice - Peppercorn Melange', 521.82, 35),
(2, 'Scallops - 10/20', 443.44, 59),
(1, 'Fish - Bones', 113.59, 74),
(2, 'Island Oasis - Magarita Mix', 281.79, 5);

insert into clients (first_name, last_name, phone_number, district_id, address) values
('Arleyne', 'Crotch', '4249328283', 8, '31739 Scott Drive'),
('Vinny', 'Buckingham', '4313988521', 10, '5 Rowland Street'),
('Kellia', 'Pakeman', '1071536087', 9, '022 Westend Center'),
('Elnora', 'Fallows', '1371280446', 6, '40 Eliot Trail'),
('Travis', 'Liptrod', '4746859534', 4, '61059 Grim Way'),
('Phillipp', 'Havock', '1244803317', 6, '865 Hovde Trail'),
('Clarine', 'Canero', '2103286631', 9, '52084 Anhalt Pass'),
('Nickolaus', 'West', '2106108169', 5, '582 Ludington Hill'),
('Benni', 'Youel', '1203091967', 1, '85331 Mcbride Street'),
('Clarissa', 'Dutson', '1887254030', 3, '05 Anzinger Alley'),
('Germain', 'Winney', '7971153671', 1, '7 Sullivan Court'),
('Effie', 'Livingston', '9604413203', 2, '587 Summer Ridge Lane'),
('Orlando', 'McGoldrick', '7617674904', 5, '423 Sage Hill'),
('Yetta', 'Whettleton', '3943583403', 9, '3 Shelley Road'),
('Britt', 'Kaye', '9697865395', 9, '7472 Merry Drive');

insert into statuses (id, status) values
(1, 'создан'),
(2, 'оплачен'),
(3, 'собран'),
(4, 'передан в доставку'),
(5, 'доставлен');

insert into orders (client_id, shop_id, purchase_date, status_id, courier_id) values
(6, 1, '2021-7-1T8:43:28', 4, 2),
(7, 1, '2021-8-1T8:43:28', 2, 4),
(9, 1, '2021-9-1T8:43:28', 2, 6),
(1, 1, '2021-6-1T8:43:28', 5, 7),
(9, 1, '2022-5-1T8:43:28', 1, 9),
(12, 1,'2022-1-1T8:43:28', 4, 10),
(2, 1, '2022-2-1T8:43:28', 5, 2),
(12, 1,'2022-3-1T8:43:28', 1, 4),
(11, 1,'2022-4-1T8:43:28', 2, 6),
(12, 1,'2022-5-1T8:43:28', 3, 7),
(4, 1, '2022-5-1T8:43:28', 3, 9),
(13, 2,'2022-3-1T8:43:28', 3, 1),
(5, 2, '2022-4-1T8:43:28', 1, 3),
(9, 2, '2022-2-1T8:43:28', 2, 8);

insert into orders_products (order_id, product_id, quantity) values
(1, 3, 4),
(8, 19, 1),
(2, 3, 4),
(1, 12, 8),
(1, 13, 4),
(11, 3, 7),
(4, 7, 8),
(3, 2, 1),
(8, 12, 5),
(4, 3, 3),
(12, 9, 1),
(12, 10, 3),
(13, 17, 3),
(14, 1, 8),
(14, 9, 4),
(13, 9, 2),
(12, 20, 4),
(12, 1, 2);