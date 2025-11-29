from flask import *
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from datetime import datetime, date, timedelta
from decimal import Decimal

# инициализация приложения и базы данных
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mainDB.db'
db = SQLAlchemy(app)

# инициализация менеджера авторизации
login_manager = LoginManager()
login_manager.login_view = 'login_post'
login_manager.init_app(app)

# загрузка конкретного пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Таблица тарифов
class Tariff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Название тарифа
    cost = db.Column(db.Numeric(10, 2), nullable=False) # Стоимость тарифа при первой покупке
    deposit_per_book = db.Column(db.Numeric(10, 2), nullable=False) # Депозит за 1 книгу при данном тарифе
    rental_days = db.Column(db.Integer, nullable=False) # Количество дней аренды книги при данном тарифе
    penalty_per_day = db.Column(db.Numeric(10, 2), nullable=False) # Штраф за просрочку аренды при данном тарифе

    # Связь с пользователями
    users = db.relationship('User', backref='tariff', lazy=True)

# Таблица пользователей
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(255), nullable=False) # Фамилия
    first_name = db.Column(db.String(255), nullable=False) # Имя
    patronymic = db.Column(db.String(255)) # Отчество
    email = db.Column(db.String(255), unique=True, nullable=False) # Почта
    phone = db.Column(db.String(20), nullable=False) # Телефон
    password_hash = db.Column(db.String(255), nullable=False) # Пароль (в хэш через wekzeug)
    deposit = db.Column(db.Numeric(10, 2), default=0.00) # Текущий баланс счета
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Времядата создания аккаунта

    # Внешние ключи
    tariff_id = db.Column(db.Integer, db.ForeignKey('tariff.id')) # Тариф, выбранный пользователем

    # Связи
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    deposit_transactions = db.relationship('DepositTransaction', backref='user', lazy=True)

# Таблица филиалов
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False) # Название филиала
    address = db.Column(db.Text, nullable=False) # Адрес

    # Связи
    orders = db.relationship('Order', backref='branch', lazy=True)

# Таблица книг
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False) # Название книги
    author = db.Column(db.String(255), nullable=False) # Автор книги
    genre = db.Column(db.String(100), nullable=False)  # Жанр
    language = db.Column(db.String(50), nullable=False, default='Русский')  # Язык
    publisher = db.Column(db.String(255))  # Издательство
    description = db.Column(db.Text)  # Описание книги
    image_url = db.Column(db.String(500))  # URL для обложки
    is_available = db.Column(db.Boolean, default=True, nullable=False)  # Доступна ли книга для аренды

    # Связи
    cart_items = db.relationship('CartItem', backref='book', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='book', lazy=True)

# Таблица корзины
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow) # Датавремя добавления

    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Пользователь, которому принадлежит корзина
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False) # Конкретная книга в корзине

# Таблица заказов
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_deposit = db.Column(db.Numeric(10, 2), nullable=False) # Общая сумма заказа
    status = db.Column(db.Enum('assembling', 'delivery', 'delivered', 'returned', name='order_status'), default='assembling') # Статус заказа: в сборке, в доставке, доставлен, возвращен
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Датавремя создания заказа
    picked_up_at = db.Column(db.DateTime) # Датавремя забирания заказа пользователем из филиала
    due_return_date = db.Column(db.Date) # Дата конца аренды
    actual_return_date = db.Column(db.Date) # Дата возвращения заказа пользователем
    penalty_amount = db.Column(db.Numeric(10, 2), default=0.00) # Сумма штрафа за просрочку

    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Пользователь, которому принадлежит заказ
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False) # Филиал, в который оформлен заказ

    # Связи
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    deposit_transactions = db.relationship('DepositTransaction', backref='order', lazy=True)

# Таблица элементов заказа
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    damage_ratio = db.Column(db.Enum('0', '1', '2', name='damage_ratio_enum'), default='0') # Уровень повреждения книги, меняется при возвращении заказа, по стандарту из магазина все книги всегда 0, по возвращении оценка: 0 - не повреждена (без штрафов), 1 - повреждена (снимается 1/2 депозита за эту одну книгу), 2 - не подлежит восстановлению (снимается полный депозит за эту книгу)

    # Внешние ключи
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False) # Заказ, в котором содержится эта книга
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False) # Сама книга из базы

# Таблица операций с депозитом
class DepositTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('topup', 'withdrawal', 'block', 'charge', 'unblock', name='transaction_type'), nullable=False) # Тип операции с депозитом
    amount = db.Column(db.Numeric(10, 2), nullable=False) # Сумма операции
    description = db.Column(db.Text) # Описание операции
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Датавремя проведения операции

    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Пользователь, к которому относится операция
    order_id = db.Column(db.Integer, db.ForeignKey('order.id')) # Заказ, по которому проводится операция

# Создание начальных данных
def create_initial_data():
    # Тарифы
    tariffs = [
        Tariff(name='Стандарт', cost=10000, deposit_per_book=2000, rental_days=14, penalty_per_day=500),
        Tariff(name='Продвинутый', cost=20000, deposit_per_book=1500, rental_days=21, penalty_per_day=300),
        Tariff(name='Премиум', cost=30000, deposit_per_book=1000, rental_days=30, penalty_per_day=200)
    ]

    # Филиалы
    branches = [
        Branch(name='Центральный филиал', address='ул. Главная, д. 1'),
        Branch(name='Северный филиал', address='ул. Северная, д. 25'),
        Branch(name='Южный филиал', address='ул. Южная, д. 15')
    ]

    db.session.add_all(tariffs)
    db.session.add_all(branches)
    db.session.commit()

# Функции рендера страниц и обработки форм

# Вспомогательная функция для проверки доступности книги
def is_book_available(book_id):
    """Проверяет, доступна ли книга для аренды (не находится в активном заказе)"""
    book = Book.query.get(book_id)
    if not book:
        return False
    
    # Сначала проверяем поле is_available в БД
    if not book.is_available:
        return False
    
    # Затем проверяем, есть ли книга в активных заказах (не возвращенных)
    active_order_items = OrderItem.query.join(Order).filter(
        OrderItem.book_id == book_id,
        Order.status != 'returned'
    ).first()
    return active_order_items is None

# Главная страница
@app.route("/")
@app.route("/index.html")
def index():
    # Получаем несколько книг для отображения на главной
    featured_books = Book.query.limit(3).all()
    # Проверяем доступность каждой книги
    for book in featured_books:
        book.is_available = is_book_available(book.id)
    return render_template("index.html", current_user=current_user, featured_books=featured_books)

# Страница библиотеки
@app.route("/booklist.html")
def booklist():
    books = Book.query.all()
    # Проверяем доступность каждой книги
    for book in books:
        book.is_available = is_book_available(book.id)
    return render_template("booklist.html", current_user=current_user, books=books)

# Страница отдельной книги
@app.route("/book.html/<int:book_id>", methods=['GET', 'POST'])
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Проверяем доступность книги
    book.is_available = is_book_available(book_id)

    if request.method == 'POST' and current_user.is_authenticated:
        action = request.form.get('action')
        if action == 'Добавить в корзину':
            # Проверяем доступность книги
            if not book.is_available:
                flash('Книга недоступна для аренды')
                return redirect(url_for('book_detail', book_id=book_id))
            
            # Проверяем, не добавлена ли уже книга в корзину
            existing_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
            if not existing_item:
                cart_item = CartItem(user_id=current_user.id, book_id=book_id)
                db.session.add(cart_item)
                db.session.commit()
                flash('Книга добавлена в корзину')
            else:
                flash('Книга уже в корзине')
            return redirect(url_for('cart', book_id=book_id))

    # Рассчитываем залог и срок аренды для авторизованных пользователей
    deposit = None
    rental_days = None
    if current_user.is_authenticated and current_user.tariff:
        deposit = float(current_user.tariff.deposit_per_book)
        rental_days = current_user.tariff.rental_days

    return render_template("book.html", current_user=current_user, book=book, deposit=deposit, rental_days=rental_days)

# Страница корзины
@app.route("/cart.html", methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'Удалить':
            book_id = request.form.get('book_id')
            cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                flash('Книга удалена из корзины')
            return redirect(url_for('cart'))

        elif action == 'Оформить заказ':
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            if not cart_items:
                flash('Корзина пуста')
                return redirect(url_for('cart'))

            # Проверяем наличие тарифа
            if not current_user.tariff:
                flash('Необходимо выбрать тариф')
                return redirect(url_for('signup_post'))

            # Получаем выбранный филиал
            branch_id = request.form.get('branch_id')
            if not branch_id:
                flash('Выберите филиал для доставки')
                return redirect(url_for('cart'))
            
            try:
                branch_id = int(branch_id)
            except (ValueError, TypeError):
                flash('Неверный филиал')
                return redirect(url_for('cart'))
            
            branch = Branch.query.get(branch_id)
            if not branch:
                flash('Выбранный филиал не найден')
                return redirect(url_for('cart'))

            # Рассчитываем общий депозит
            total_deposit = Decimal(0)
            for item in cart_items:
                total_deposit += current_user.tariff.deposit_per_book

            # Проверяем баланс пользователя
            if float(current_user.deposit) < float(total_deposit):
                flash('Недостаточно средств на счету')
                return redirect(url_for('cart'))

            due_return_date = date.today() + timedelta(days=current_user.tariff.rental_days)

            new_order = Order(
                user_id=current_user.id,
                branch_id=branch_id,
                total_deposit=total_deposit,
                due_return_date=due_return_date,
                status='assembling'
            )
            db.session.add(new_order)
            db.session.flush()  # Получаем ID заказа

            # Создаем элементы заказа
            for item in cart_items:
                order_item = OrderItem(order_id=new_order.id, book_id=item.book_id)
                db.session.add(order_item)

            # Блокируем средства
            current_user.deposit -= total_deposit
            deposit_transaction = DepositTransaction(
                user_id=current_user.id,
                order_id=new_order.id,
                type='block',
                amount=total_deposit,
                description=f'Блокировка средств за заказ #{new_order.id}'
            )
            db.session.add(deposit_transaction)

            # Очищаем корзину
            for item in cart_items:
                db.session.delete(item)

            db.session.commit()
            flash('Заказ успешно оформлен')
            return redirect(url_for('profile'))

    # GET запрос - отображаем корзину
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Получаем список филиалов для выбора
    branches = Branch.query.all()
    
    if not cart_items:
        return render_template("cart.html", current_user=current_user, cart_items=None, total_deposit=0, rental_days=0, branches=branches)
    
    # Рассчитываем общий депозит и срок аренды
    total_deposit = Decimal(0)
    if current_user.tariff:
        for item in cart_items:
            total_deposit += current_user.tariff.deposit_per_book
        rental_days = current_user.tariff.rental_days
    else:
        rental_days = 0
    
    return render_template("cart.html", current_user=current_user, cart_items=cart_items, 
                         total_deposit=float(total_deposit), rental_days=rental_days, branches=branches)

# Страница профиля
@app.route("/profile.html")
@login_required
def profile():
    # Активные заказы (не возвращенные)
    current_orders = Order.query.filter_by(user_id=current_user.id).filter(
        Order.status != 'returned'
    ).order_by(Order.created_at.desc()).all()

    # История заказов (возвращенные)
    order_history = Order.query.filter_by(user_id=current_user.id).filter(
        Order.status == 'returned'
    ).order_by(Order.created_at.desc()).all()

    return render_template("profile.html", current_user=current_user,
                         current_orders=current_orders, order_history=order_history)

# Страница заказа
@app.route("/order.html/<int:order_id>")
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    # Проверяем, что заказ принадлежит текущему пользователю
    if order.user_id != current_user.id:
        flash('Доступ запрещен')
        return redirect(url_for('profile'))

    # Получаем книги из заказа
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    books = [item.book for item in order_items]

    # Форматируем даты
    created_date = order.created_at.strftime('%d.%m.%Y') if order.created_at else None
    start_date = order.picked_up_at.strftime('%d.%m.%Y') if order.picked_up_at else None
    end_date = order.due_return_date.strftime('%d.%m.%Y') if order.due_return_date else None

    # Статусы на русском
    status_map = {
        'assembling': 'В сборке',
        'delivery': 'В доставке',
        'delivered': 'Доставлен',
        'returned': 'Возвращен'
    }
    status_ru = status_map.get(order.status, order.status)

    return render_template("order.html", current_user=current_user, order=order,
                         books=books, created_date=created_date, start_date=start_date,
                         end_date=end_date, status_ru=status_ru, branch=order.branch)

# Страница кошелька
@app.route("/wallet.html", methods=['GET', 'POST'])
@login_required
def wallet():
    if request.method == 'POST':
        action = request.form.get('action')
        amount = request.form.get('amount')

        if not amount:
            flash('Укажите сумму')
            return redirect(url_for('wallet'))

        try:
            amount = Decimal(amount)
            if amount <= 0:
                flash('Сумма должна быть положительной')
                return redirect(url_for('wallet'))
        except:
            flash('Неверный формат суммы')
            return redirect(url_for('wallet'))

        if action == 'deposit':
            # Пополнение счета
            current_user.deposit += amount
            transaction = DepositTransaction(
                user_id=current_user.id,
                type='topup',
                amount=amount,
                description=f'Пополнение счета на {amount} у.е.'
            )
            db.session.add(transaction)
            db.session.commit()
            flash(f'Счет пополнен на {amount} у.е.')
            return redirect(url_for('wallet'))

        elif action == 'withdraw':
            # Вывод средств
            # Рассчитываем доступный баланс (баланс минус заблокированные средства)
            blocked_amount = Decimal(0)
            active_orders = Order.query.filter_by(user_id=current_user.id).filter(
                Order.status != 'returned'
            ).all()
            for order in active_orders:
                blocked_amount += order.total_deposit

            available_balance = Decimal(str(current_user.deposit)) - blocked_amount

            if amount > available_balance:
                flash(f'Недостаточно средств. Доступно: {available_balance} у.е.')
                return redirect(url_for('wallet'))

            current_user.deposit -= amount
            transaction = DepositTransaction(
                user_id=current_user.id,
                type='withdrawal',
                amount=amount,
                description=f'Вывод средств {amount} у.е.'
            )
            db.session.add(transaction)
            db.session.commit()
            flash(f'Выведено {amount} у.е.')
            return redirect(url_for('wallet'))

    # GET запрос - отображаем кошелек
    # Рассчитываем заблокированные средства
    blocked_amount = Decimal(0)
    active_orders = Order.query.filter_by(user_id=current_user.id).filter(
        Order.status != 'returned'
    ).all()

    orders_with_deposits = []
    for order in active_orders:
        blocked_amount += order.total_deposit
        orders_with_deposits.append({
            'id': order.id,
            'deposit': float(order.total_deposit),
            'end_date': order.due_return_date.strftime('%d.%m.%Y') if order.due_return_date else None
        })

    available_balance = Decimal(str(current_user.deposit)) - blocked_amount

    # Получаем историю операций
    transactions = DepositTransaction.query.filter_by(user_id=current_user.id).order_by(
        DepositTransaction.created_at.desc()
    ).limit(10).all()

    return render_template("wallet.html", current_user=current_user,
                         blocked_amount=float(blocked_amount),
                         available_balance=float(available_balance),
                         current_orders=orders_with_deposits,
                         transactions=transactions)

# Форма регистрации
@app.route("/signup.html", methods=['GET', 'POST'])
def signup_post():
    if request.method == 'POST':
        surname = request.form.get('surname')
        name = request.form.get('name')
        patron = request.form.get('patron')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        tariff = request.form.get('tariff')

        # Проверяем, что все поля заполнены
        if not all([surname, name, patron, email, password, phone, tariff]):
            flash('Заполните все обязательные поля')
            return redirect(url_for('signup_post'))

        # Проверка существующего пользователя
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Пользователь с таким e-mail уже зарегистрирован')
            return redirect(url_for('signup_post'))

        # Определяем тариф
        tariff_map = {
            'standard': 1,  # Стандарт
            'pro': 2,       # Расширенный
            'premium': 3    # Премиум
        }
        tariff_id = tariff_map.get(tariff)
        if not tariff_id:
            flash('Выберите тариф')
            return redirect(url_for('signup_post'))

        # Создаем пользователя
        new_user = User(
            last_name=surname,
            first_name=name,
            patronymic=patron,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            tariff_id=tariff_id,
            deposit=0
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация успешна. Войдите в систему.')
            return redirect(url_for('login_post'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации')
            return redirect(url_for('signup_post'))

    # GET запрос - показываем форму
    tariffs = Tariff.query.all()
    return render_template("signup.html", tariffs=tariffs)

# Форма авторизации
@app.route("/login.html", methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Неверный email или пароль')
            return redirect(url_for('login_post'))

        login_user(user, remember=remember)
        return redirect(url_for('profile'))

    return render_template("login.html")

# Выход
@app.route("/logout.html")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    else:
        cart_count = 0
    return dict(cart_count=cart_count)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)

# Запуск базы данных:
# from app import app, db
# app.app_context().push()
# db.create_all()
# create_initial_data()