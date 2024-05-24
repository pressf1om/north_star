import requests
# Имитация приложения водителя

status_car_now = ''


# GET
def get(number_car):
    global status_car_now
    url = f"http://127.0.0.1:5000/api/applications/{number_car}"  # кодирование пробела в URL
    response = requests.get(url)
    data = response.json()
    print(data)
    if response.json()['status'] == '1':
        status_car_now = 'Свободна'
    if response.json()['status'] == '2':
        status_car_now = 'Назначена'
    if response.json()['status'] == '3':
        status_car_now = 'Прибыла на погрузку'
    if response.json()['status'] == '4':
        status_car_now = 'Погружена'
    if response.json()['status'] == '5':
        status_car_now = 'Транзит'
    if response.json()['status'] == '6':
        status_car_now = 'Прибыла на выгрузку'
    if response.json()['status'] == '7':
        status_car_now = 'Выгружена'
    if response.json()['status'] == '8':
        status_car_now = 'Завершение рейса'
    if response.json()['status'] == '9':
        status_car_now = 'На Т.О.'

    print(f'Машина {number_car}, статус {status_car_now}')


# POST
def post(number_car, status_):
    url = f"http://127.0.0.1:5000/api/applications/{number_car}"  # кодирование пробела в URL
    # JSON-тело запроса
    payload = {
        "new_status": f"{status_}"
    }

    # Отправка POST-запроса
    response = requests.post(url, json=payload)

    # Проверка статуса ответа
    if response.status_code == 200:
        print('Status updated successfully')
    else:
        print('Failed to update status:', response.text)


print('Добро пожаловать в northstar-logistics! Это имитация функционала мобильного приложения водителя.')
print("Вы можете узнать статус заявки, изменять их.")
print("Для того, чтобы выбрать заявку, введите номер машины, которая ее выполняет")
input_user_number_car = input('Номер (Точно также как и на сайте): ')

input_user_number_car.replace(' ', "%20")

get(input_user_number_car)
post(input_user_number_car, 2)


if status_car_now == 'Назначена':
    print('Вы доехали до места погрузки?')
    a = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if a == 1:
        post(input_user_number_car, 3)
        get(input_user_number_car)
    else:
        print("Доезжайте.")
if status_car_now == 'Прибыла на погрузку':
    print('Вы загрузились?')
    a = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if a == 1:
        post(input_user_number_car, 4)
        get(input_user_number_car)
    else:
        print("Грузитесь.")
if status_car_now == 'Погружена':
    print('Вы в пути?')
    a = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if a == 1:
        post(input_user_number_car, 5)
        get(input_user_number_car)
    else:
        print("Готовьтесь к выезду.")
if status_car_now == 'Транзит':
    print('Вы доехали до выгрузки?')
    a = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if a == 1:
        post(input_user_number_car, 6)
        get(input_user_number_car)
    else:
        print("Едте.")
if status_car_now == 'Прибыла на выгрузку':
    print('Вы выгрузились?')
    a = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if a == 1:
        post(input_user_number_car, 7)
        get(input_user_number_car)
    else:
        print("Выгружайтесь.")
if status_car_now == 'Выгружена':
    print('Вы готовы завершить рейс?')
    a = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if a == 1:
        post(input_user_number_car, 8)
        get(input_user_number_car)
    else:
        print('Вам нужно тех. обслуживание?')
        b = int(input('1 - Да, 2 - Нет, Введите цифру: '))
        if b == 1:
            post(input_user_number_car, 9)
            print("Мы уведомили об этом администратора")
        else:
            post(input_user_number_car, 9)
            get(input_user_number_car)
            print('Завершайте рейс')
if status_car_now == 'На Т.О.':
    print('Вы обслужили машину?')
    c = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if c == 1:
        post(input_user_number_car, 1)
        print("Ждите новый рейс")
    else:
        print('Обратитесь к администратору')
if status_car_now == 'Завершение рейса':
    print('Вы готовы ехать дальше?')
    r = int(input('1 - Да, 2 - Нет, Введите цифру: '))
    if r == 1:
        post(input_user_number_car, 1)
        print("Ждите новый рейс")
    else:
        print('Обратитесь к администратору')


