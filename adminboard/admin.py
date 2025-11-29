from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, date
from decimal import Decimal
import sys
import os

# Добавляем родительскую директорию в путь для импорта моделей
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Меняем рабочую директорию на родительскую для импорта app
original_cwd = os.getcwd()
os.chdir(parent_dir)

# Импортируем модели и БД из основного приложения
from app import db, User, Book, Order, OrderItem, Tariff, DepositTransaction, Branch

# Меняем директорию на исходную
os.chdir(original_cwd)

# Инициализируем Flask приложение для админки
app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin-secret-key-here'

# НАСТРОЙКИ СЕССИИ ДЛЯ АДМИНКИ
app.config['SESSION_COOKIE_NAME'] = 'admin_session'  # Уникальное имя для админки
app.config['SESSION_COOKIE_PATH'] = '/'  # Путь для куки
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # False для разработки
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 час в секундах

# Путь к базе данных - используем тот же, что и основное приложение
# Основное приложение использует 'sqlite:///mainDB.db' который Flask помещает в папку instance
# Нам нужно использовать тот же путь
db_path = os.path.join(parent_dir, 'instance', 'mainDB.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Экземпляр БД из app.py уже создан и привязан к основному приложению
# Нам нужно также привязать его к этому админ-приложению чтобы он работал в контексте админки
# Flask-SQLAlchemy поддерживает привязку к нескольким приложениям
db.init_app(app)

# Пароль администратора (по умолчанию: 12345)
ADMIN_PASSWORD = "12345"

def admin_required(f):
    """Декоратор для требования входа администратора"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def admin_login():
    """Страница входа администратора"""
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный пароль')

    return render_template('login.html')

@app.route('/logout')
def admin_logout():
    """Выход администратора"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/dashboard')
@admin_required
def dashboard():
    """Панель управления администратора"""
    return render_template('dashboard.html')

@app.route('/api/add_book', methods=['POST'])
@admin_required
def add_book():
    """Добавить новую книгу в базу данных"""
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        language = request.form.get('language', 'Русский')
        publisher = request.form.get('publisher', '')
        description = request.form.get('description', '')
        image_url = request.form.get('image_url', '')

        if not all([title, author, genre]):
            return jsonify({'success': False, 'message': 'Заполните все обязательные поля'})

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            language=language,
            publisher=publisher,
            description=description,
            image_url=image_url
        )

        db.session.add(new_book)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Книга успешно добавлена'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

@app.route('/api/search_users', methods=['POST'])
@admin_required
def search_users():
    """Поиск пользователей по имени и фамилии"""
    try:
        search_query = request.form.get('query', '').strip()

        if not search_query:
            return jsonify({'success': False, 'message': 'Введите имя или фамилию'})

        # Поиск по имени или фамилии
        users = User.query.filter(
            (User.first_name.ilike(f'%{search_query}%')) |
            (User.last_name.ilike(f'%{search_query}%'))
        ).all()

        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'patronymic': user.patronymic or '',
                'email': user.email,
                'phone': user.phone,
                'deposit': float(user.deposit),
                'tariff_id': user.tariff_id,
                'tariff_name': user.tariff.name if user.tariff else 'Не выбран'
            })

        return jsonify({'success': True, 'users': users_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

@app.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    """Страница деталей пользователя с заказами и опциями управления"""
    user = User.query.get_or_404(user_id)
    tariffs = Tariff.query.all()
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    return render_template('user_detail.html', user=user, tariffs=tariffs, orders=orders)

@app.route('/api/change_tariff', methods=['POST'])
@admin_required
def change_tariff():
    """Изменить тариф пользователя"""
    try:
        user_id = request.form.get('user_id')
        tariff_id = request.form.get('tariff_id')

        user = User.query.get_or_404(user_id)
        tariff = Tariff.query.get_or_404(tariff_id)

        user.tariff_id = tariff_id
        db.session.commit()

        return jsonify({'success': True, 'message': f'Тариф изменен на {tariff.name}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

@app.route('/api/change_order_status', methods=['POST'])
@admin_required
def change_order_status():
    """Изменить статус заказа"""
    try:
        order_id = request.form.get('order_id')
        new_status = request.form.get('status')

        order = Order.query.get_or_404(order_id)

        valid_statuses = ['assembling', 'delivery', 'delivered', 'returned']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Неверный статус'})

        # Если статус устанавливается в 'delivered', устанавливаем picked_up_at
        if new_status == 'delivered' and not order.picked_up_at:
            order.picked_up_at = datetime.utcnow()

        # Если статус устанавливается в 'returned', устанавливаем actual_return_date
        if new_status == 'returned' and not order.actual_return_date:
            order.actual_return_date = date.today()

        order.status = new_status
        db.session.commit()

        return jsonify({'success': True, 'message': 'Статус заказа изменен'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

@app.route('/order/<int:order_id>')
@admin_required
def order_detail(order_id):
    """Страница деталей заказа для оценки повреждений"""
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    return render_template('order_detail.html', order=order, order_items=order_items)

@app.route('/api/assess_damage', methods=['POST'])
@admin_required
def assess_damage():
    """Оценить повреждения для элементов заказа и закрыть заказ"""
    try:
        order_id = request.form.get('order_id')
        order = Order.query.get_or_404(order_id)

        # Получаем все элементы заказа
        order_items = OrderItem.query.filter_by(order_id=order_id).all()

        # Получаем тариф пользователя для расчета депозита за книгу
        user = order.user
        if not user.tariff:
            return jsonify({'success': False, 'message': 'У пользователя не выбран тариф'})

        deposit_per_book = user.tariff.deposit_per_book
        total_fee = Decimal(0)

        # Обновляем коэффициенты повреждений и рассчитываем штрафы
        for item in order_items:
            damage_key = f'damage_{item.id}'
            damage_ratio = request.form.get(damage_key, '0')

            if damage_ratio not in ['0', '1', '2']:
                damage_ratio = '0'

            item.damage_ratio = damage_ratio

            # Рассчитываем штраф на основе повреждений
            if damage_ratio == '1':
                # Повреждена: 1/2 депозита
                total_fee += deposit_per_book / 2
            elif damage_ratio == '2':
                # Не подлежит восстановлению: полный депозит
                total_fee += deposit_per_book

        # Рассчитываем сумму возврата
        return_amount = order.total_deposit - total_fee

        # Обновляем статус заказа
        order.status = 'returned'
        order.actual_return_date = date.today()

        # Возвращаем депозит пользователю (разблокируем и возвращаем остаток)
        # Сначала разблокируем полный депозит (добавляем обратно на баланс пользователя)
        user.deposit += order.total_deposit
        unblock_transaction = DepositTransaction(
            user_id=user.id,
            order_id=order.id,
            type='unblock',
            amount=order.total_deposit,
            description=f'Разблокировка депозита за заказ #{order.id}'
        )
        db.session.add(unblock_transaction)

        # Затем списываем штраф если есть (вычитаем из депозита пользователя)
        if total_fee > 0:
            user.deposit -= total_fee
            charge_transaction = DepositTransaction(
                user_id=user.id,
                order_id=order.id,
                type='charge',
                amount=total_fee,
                description=f'Штраф за повреждения по заказу #{order.id}'
            )
            db.session.add(charge_transaction)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Заказ закрыт. Возвращено: {float(return_amount):.2f} у.е., Штраф: {float(total_fee):.2f} у.е.',
            'user_id': user.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True, use_reloader=False)

