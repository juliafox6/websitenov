PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE tariff (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	cost NUMERIC(10, 2) NOT NULL, 
	deposit_per_book NUMERIC(10, 2) NOT NULL, 
	rental_days INTEGER NOT NULL, 
	penalty_per_day NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO tariff VALUES(1,'Стандарт',10000,2000,14,500);
INSERT INTO tariff VALUES(2,'Продвинутый',20000,1500,21,300);
INSERT INTO tariff VALUES(3,'Премиум',30000,1000,30,200);
CREATE TABLE branch (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	address TEXT NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO branch VALUES(1,'Центральный филиал','ул. Главная, д. 1');
INSERT INTO branch VALUES(2,'Северный филиал','ул. Северная, д. 25');
INSERT INTO branch VALUES(3,'Южный филиал','ул. Южная, д. 15');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	last_name VARCHAR(255) NOT NULL, 
	first_name VARCHAR(255) NOT NULL, 
	patronymic VARCHAR(255), 
	email VARCHAR(255) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	deposit NUMERIC(10, 2), 
	created_at DATETIME, 
	tariff_id INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	FOREIGN KEY(tariff_id) REFERENCES tariff (id)
);
INSERT INTO user VALUES(1,'admin','admin','admin','admin@admin.com','+79286249180','scrypt:32768:8:1$9u21DuBwNXXBzTQW$bb188ae922f97438a18d3ecc12c49a8a35bd24162cfb4cc0fcbfaa805d8656c8367e4a4c3652422995cdc9bb74f409187209eb83b90780afd236b6709a0d6f53',26000,'2025-11-28 19:46:20.156613',1);
INSERT INTO user VALUES(2,'test','test','test','test@test.com','80000000000','scrypt:32768:8:1$ty4tM5lS7dEWaBKz$73eed1d829dfe321b7639e5614251bd6e6e16988a38ea7183b5265d6e0c50e135a10b293d369c5d56469fc309f6c5d5c2651ad8843605a5a8b2c13ec6b032a1d',0,'2025-11-28 21:04:55.660637',3);
CREATE TABLE cart_item (
	id INTEGER NOT NULL, 
	added_at DATETIME, 
	user_id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(book_id) REFERENCES book (id)
);
INSERT INTO cart_item VALUES(1,'2025-11-29 11:28:34.518928',1,2);
CREATE TABLE IF NOT EXISTS "order" (
	id INTEGER NOT NULL, 
	total_deposit NUMERIC(10, 2) NOT NULL, 
	status VARCHAR(10), 
	created_at DATETIME, 
	picked_up_at DATETIME, 
	due_return_date DATE, 
	actual_return_date DATE, 
	penalty_amount NUMERIC(10, 2), 
	user_id INTEGER NOT NULL, 
	branch_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(branch_id) REFERENCES branch (id)
);
INSERT INTO "order" VALUES(1,4000,'returned','2025-11-29 10:58:38.726550','2025-11-29 10:59:42.055369','2025-12-13','2025-11-29',0,1,1);
INSERT INTO "order" VALUES(2,2000,'assembling','2025-11-29 11:25:34.325538',NULL,'2025-12-13',NULL,0,1,2);
CREATE TABLE order_item (
	id INTEGER NOT NULL, 
	damage_ratio VARCHAR(1), 
	order_id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES "order" (id), 
	FOREIGN KEY(book_id) REFERENCES book (id)
);
INSERT INTO order_item VALUES(1,'0',1,3);
INSERT INTO order_item VALUES(2,'0',1,6);
INSERT INTO order_item VALUES(3,'0',2,1);
CREATE TABLE deposit_transaction (
	id INTEGER NOT NULL, 
	type VARCHAR(10) NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	user_id INTEGER NOT NULL, 
	order_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(order_id) REFERENCES "order" (id)
);
INSERT INTO deposit_transaction VALUES(1,'topup',10000,'Пополнение счета на 10000 у.е.','2025-11-28 19:47:40.689331',1,NULL);
INSERT INTO deposit_transaction VALUES(2,'withdrawal',10000,'Вывод средств 10000 у.е.','2025-11-28 19:47:54.010891',1,NULL);
INSERT INTO deposit_transaction VALUES(3,'topup',50000,'Пополнение счета на 50000 у.е.','2025-11-28 20:26:35.277067',1,NULL);
INSERT INTO deposit_transaction VALUES(4,'block',4000,'Блокировка средств за заказ #1','2025-11-28 20:26:40.372581',1,1);
INSERT INTO deposit_transaction VALUES(5,'unblock',4000,'Разблокировка депозита за заказ #1','2025-11-28 20:28:44.801784',1,1);
INSERT INTO deposit_transaction VALUES(6,'charge',1000,'Штраф за повреждения по заказу #1','2025-11-28 20:28:44.801794',1,1);
INSERT INTO deposit_transaction VALUES(7,'block',4000,'Блокировка средств за заказ #2','2025-11-28 20:49:36.051901',1,2);
INSERT INTO deposit_transaction VALUES(8,'unblock',4000,'Разблокировка депозита за заказ #2','2025-11-28 20:51:16.154195',1,2);
INSERT INTO deposit_transaction VALUES(9,'charge',3000,'Штраф за повреждения по заказу #2','2025-11-28 20:51:16.154204',1,2);
INSERT INTO deposit_transaction VALUES(10,'topup',20000,'Пополнение счета на 20000 у.е.','2025-11-28 20:51:28.682885',1,NULL);
INSERT INTO deposit_transaction VALUES(11,'withdrawal',30000,'Вывод средств 30000 у.е.','2025-11-28 20:51:32.801952',1,NULL);
INSERT INTO deposit_transaction VALUES(12,'block',6000,'Блокировка средств за заказ #3','2025-11-28 20:53:51.101736',1,3);
INSERT INTO deposit_transaction VALUES(13,'withdrawal',5000,'Вывод средств 5000 у.е.','2025-11-28 21:05:52.814148',1,NULL);
INSERT INTO deposit_transaction VALUES(14,'topup',8000,'Пополнение счета на 8000 у.е.','2025-11-28 21:05:58.590417',1,NULL);
INSERT INTO deposit_transaction VALUES(15,'block',6000,'Блокировка средств за заказ #4','2025-11-28 21:06:02.628092',1,4);
INSERT INTO deposit_transaction VALUES(16,'unblock',6000,'Разблокировка депозита за заказ #3','2025-11-28 21:07:11.830462',1,3);
INSERT INTO deposit_transaction VALUES(17,'charge',3000,'Штраф за повреждения по заказу #3','2025-11-28 21:07:11.830472',1,3);
INSERT INTO deposit_transaction VALUES(18,'block',2000,'Блокировка средств за заказ #5','2025-11-29 09:43:50.239215',1,5);
INSERT INTO deposit_transaction VALUES(19,'block',4000,'Блокировка средств за заказ #1','2025-11-29 10:58:38.730854',1,1);
INSERT INTO deposit_transaction VALUES(20,'unblock',4000,'Разблокировка депозита за заказ #1','2025-11-29 10:59:50.275686',1,1);
INSERT INTO deposit_transaction VALUES(21,'block',2000,'Блокировка средств за заказ #2','2025-11-29 11:25:34.333379',1,2);
CREATE TABLE IF NOT EXISTS "book" (
    id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    language VARCHAR(50) NOT NULL,
    publisher VARCHAR(255),
    description TEXT,
    image_url VARCHAR(500),
    is_available BOOLEAN DEFAULT 1,
    PRIMARY KEY (id)
);
INSERT INTO book VALUES(1,'Мастер и Маргарита','Михаил Булгаков','Роман','Русский','Эксмо','Мистическая история о добре и зле, любви и предательстве в сталинской Москве.','https://www.moscowbooks.ru/image/book/751/orig/i751951.jpg',1);
INSERT INTO book VALUES(2,'1984','Джордж Оруэлл','Антиутопия','Русский','Азбука','Классика антиутопии о тоталитарном обществе под постоянным контролем Большого Брата.','https://cdn.ast.ru/v2/AST000000000130417/COVER/cover1__w340.jpg',1);
INSERT INTO book VALUES(3,'Преступление и наказание','Федор Достоевский','Психологический роман','Русский','АСТ','История бывшего студента Родиона Раскольникова, совершившего убийство.','https://imo10.labirint.ru/books/729483/cover.jpg/484-0',1);
INSERT INTO book VALUES(4,'Гарри Поттер и философский камень','Джоан Роулинг','Фэнтези','Русский','Росмэн','Первая книга о приключениях юного волшебника Гарри Поттера в школе Хогвартс.','https://ir.ozone.ru/s3/multimedia-6/6366331002.jpg',1);
INSERT INTO book VALUES(5,'Властелин Колец: Братство Кольца','Дж. Р. Р. Толкин','Фэнтези','Русский','АСТ','Эпическая сага о путешествии хоббита Фродо по уничтожению Кольца Всевластья.','https://imo10.labirint.ru/books/662313/cover.jpg/484-0',1);
INSERT INTO book VALUES(6,'Три товарища','Эрих Мария Ремарк','Роман','Русский','Эксмо','История дружбы и любви троих фронтовых товарищей в послевоенной Германии.','https://imo10.labirint.ru/books/643789/cover.jpg/484-0',1);
INSERT INTO book VALUES(7,'Маленький принц','Антуан де Сент-Экзюпери','Притча','Русский','Эксмо','Философская сказка для детей и взрослых о самом важном в жизни.','https://www.moscowbooks.ru/image/book/365/orig/i365028.jpg',1);
INSERT INTO book VALUES(8,'Убить пересмешника','Харпер Ли','Роман','Русский','Азбука','История расовой несправедливости и детской невинности в американском Юге.','https://imo10.labirint.ru/books/594261/cover.jpg/242-0',1);
INSERT INTO book VALUES(9,'Шерлок Холмс: Собака Баскервилей','Артур Конан Дойл','Детектив','Русский','Эксмо','Знаменитое дело Шерлока Холмса о загадочной собье, преследующей род Баскервилей.','https://www.moscowbooks.ru/image/book/584/orig/i584706.jpg',1);
INSERT INTO book VALUES(10,'Портрет Дориана Грея','Оскар Уайльд','Классика','Русский','АСТ','История молодого человека, чей портрет стареет вместо него, вбирая все грехи.','https://www.moscowbooks.ru/image/book/564/orig/i564813.jpg',1);
COMMIT;
