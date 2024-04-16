# import
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from werkzeug.utils import redirect
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime
import sqlalchemy
import itsdangerous
from flask_login import LoginManager, login_user, login_required, logout_user


# app config
app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///north_star.db'
app.config['SECRET_KEY'] = 'north_star_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# class user for db
class User(db.Model, UserMixin):
    # айди юзера
    id = db.Column(db.Integer, primary_key=True)
    # почта
    email = db.Column(db.String(200), nullable=False)
    # логин
    username = db.Column(db.String(120), nullable=False, unique=True)
    # пароль
    password = db.Column(db.String(120), nullable=False)
    # дата регистрации
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    # статус пользователя в общей иерархии юзеров
    status = db.Column(db.String(120), nullable=False)


# class Cars for db
class Cars(db.Model, UserMixin):
    # айди машины
    id = db.Column(db.Integer, primary_key=True)
    # номер машины
    car_number = db.Column(db.String(120), nullable=False, unique=True)
    # модель машины
    model = db.Column(db.String(120), nullable=False)
    # дата регистрации
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    # статус машины
    status = db.Column(db.String(120))
    # айди текущего водителя
    car_driver_id = db.Column(db.Integer)


# необходимые переменные
data_of_roads_for_analytics = {}


# авторизация
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


# главная страница
@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    # создаются все бд на сервере
    db.create_all()

    #################################################################

    # изменение статуса машин

    # Получаем объект из базы данных
    car1 = Cars.query.filter_by(car_number='ху768й 777').first()
    car2 = Cars.query.filter_by(car_number='ху888й 71').first()
    car3 = Cars.query.filter_by(car_number='el999p 88').first()

    # Изменяем атрибуты объекта
    car1.status = 'Поездка завершена'
    car2.status = 'На базе'
    car3.status = 'В пути'

    # Зафиксируем изменения в базе данных
    db.session.commit()

    #################################################################

    # получаем айди зашедшего на сайт
    user_id = current_user.id

    # инфа о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # инфа о машинах из бд
    car_print = Cars.query.order_by(Cars.id).all()

    # достаем юзернейм для отображения в хедере
    username = temp['username']
    print(f'username = {username}')

    # разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':
        ##########################################################################

        ##########################################################################

        return render_template("home.html", data=username, car_print=car_print)
    else:
        return 'у вас недостаточно прав'


# профиль пользвателя
@app.route('/account')
@login_required
def accout():
    # получаем айди пользователя зашедшего на страницу
    user_id = current_user.id
    # забираем информацию по нему из бд для дальнейшей обработки
    user_data_in_profile = (User.query.filter_by(id=user_id).first()).__dict__
    # рендрер страницы
    return render_template("accout.html", data=user_data_in_profile)


# регистрация пользователя администратором
@app.route('/admin/add_users', methods=['POST', 'GET'])
@login_required
def add_users():
    # получаем айди пользователя зашедшего на сайт
    user_id = current_user.id

    # забираем инфу из бд по нему
    user_status = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if user_status['status'] == 'Администратор':
        if request.method == "POST":
            # получение данных из формы
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            status = request.form['status']

            # собираем объект юзер_ для регистрации в бд
            user_ = User(username=username, password=password, email=email, status=status)

            # регистрация в базе
            db.session.add(user_)
            db.session.commit()

            return redirect("/")
        else:
            return render_template("admin_add_users.html")
    else:
        return 'у вас недостаточно прав'


# регистрация машин администратором
@app.route('/admin/add_cars', methods=['POST', 'GET'])
@login_required
def add_cars():
    # получаем айди пользователя зашедшего на сайт
    user_id = current_user.id

    # забираем инфу из бд по нему
    user_status = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if user_status['status'] == 'Администратор':
        if request.method == "POST":
            # получение данных из формы
            car_number = request.form['car_number']
            model = request.form['model']

            # собираем объект юзер_ для регистрации в бд
            cars = Cars(car_number=car_number, model=model)

            # регистрация в базе
            db.session.add(cars)
            db.session.commit()

            print(f'CAR: {car_number}, {model} was created')

            return redirect("/home")
        else:
            return render_template("admin_add_cars.html")
    else:
        return 'у вас недостаточно прав'


# посмотреть всех пользвателей
@app.route("/admin/print_users")
@login_required
def print_user():
    # получаем айди пользователя зашедшего на сайт
    user_id = current_user.id

    # забираем инфу из бд по нему
    user_status = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if user_status['status'] == 'Администратор':
        user_print = User.query.order_by(User.id).all()
        return render_template("print_user.html", data=user_print)
    else:
        return 'у вас недостаточно прав'


# админ панель
@app.route("/admin")
@login_required
def admin():
    # получаем айди пользователя зашедшего на сайт
    user_id = current_user.id

    # забираем инфу из бд по нему
    user_status = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if user_status['status'] == 'Администратор':
        user_print = User.query.order_by(User.id).all()
        return render_template("admin.html", data=user_print)
    else:
        return 'у вас недостаточно прав'


# вход
@app.route('/', methods=['POST', 'GET'])
def login():
    # Если пользователь заходит не авторизованный, то ему предлагают авторизоваться
    if request.method == "GET":
        return render_template('login.html')
    else:
        # получаем отправленные данные
        login_form = request.form.get('username')
        password_form = request.form.get('password')

        # если есть и то и то
        if login_form and password_form:
            # находим совпадения в базе данных
            user_auth = User.query.filter_by(username=login_form).first()
            try:
                # извлекаем данные
                user_auth_dict = user_auth.__dict__

                # данные о пользователе в базе
                user__auth = user_auth_dict['username']
                pass__auth = user_auth_dict['password']
            except:
                print('ПОльзовтель не найден')

            # если данные совпадают, то мы авторизовываем пользователя
            if user__auth == login_form and pass__auth == password_form:
                # функция фласк логин
                login_user(user_auth)
                print(f"никнейм вошедшего: {user__auth}")
                return redirect("/home")
            else:
                return 'ошибка 1'
        else:
            return 'ошибка 2'


# выход
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # деаутендификация через фласк логин
    logout_user()
    return redirect("/")


# /current_applications


# страница добавления заявок для анализа
@app.route('/analytics_add_data', methods=['POST', 'GET'])
@login_required
def analytics_add_data():
    # получаем айди зашедшего на сайт
    user_id = current_user.id

    # инфа о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # достаем юзернейм для отображения в хедере
    username = temp['username']
    print(f'username = {username}')

    # разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':
        if request.method == "POST":
            # получение данных из формы
            number_of_road = request.form['number_of_road']
            date_start = request.form['start-date']
            date_end = request.form['end-date']
            start_coordinates = request.form['start-coordinates']
            end_coordinates = request.form['end-coordinates']
            cost = request.form['cost']

            data_of_roads_for_analytics[f'{number_of_road}'] = \
                [f'{date_start}',
                f'{date_end}',
                f'{start_coordinates}',
                f'{end_coordinates}',
                f'{cost}']

            return redirect("/analytics_add_data")
        else:
            return render_template("analytics_add_data.html", data=username)
    else:
        return 'у вас недостаточно прав'


# страница результатов анализа
@app.route('/analytics', methods=['POST', 'GET'])
@login_required
def analytics():
    # получаем айди зашедшего на сайт
    user_id = current_user.id

    # инфа о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # достаем юзернейм для отображения в хедере
    username = temp['username']
    print(f'username = {username}')

    # разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':
        # словарь со всеми зареганными заявками
        print(data_of_roads_for_analytics)
        # после кнопки выбрать, удаление словаря
        # делать через датасет
        return render_template("choosing_route.html", data_of_roads_for_analytics=data_of_roads_for_analytics)
    else:
        return 'у вас недостаточно прав'


# страница регистрации заявки
@app.route('/registration_new_application', methods=['POST', 'GET'])
@login_required
def registration_new_application():
    # получаем айди зашедшего на сайт
    user_id = current_user.id

    # инфа о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':
        if request.method == "POST":
            # получение данных из формы
            start_point = request.form['start-point']
            end_point = request.form['end-point']
            departure_date = request.form['departure-date']
            cargo_weight = request.form['cargo-weight']

            print(start_point, end_point, departure_date, cargo_weight)

            # регистрация заявок

            return redirect("/home")
        else:
            return render_template("registration_new_application.html")
    else:
        return 'у вас недостаточно прав'


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=5000)
