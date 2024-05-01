import requests
# Имитация приложения водителя


# GET
def get(number_car):
    url = f"http://northstar-logistics.ru/api/applications/{number_car}"  # кодирование пробела в URL
    response = requests.get(url)
    data = response.json()
    print(data)
    status_car_now = ''
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
    url = f"http://northstar-logistics.ru/api/applications/{number_car}"  # кодирование пробела в URL
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

print('Для того чтобы изменить статус заявки введите соотвествующую цифру из меню.')

menu = """
# статусы
# 1. Свободна
# 2. Назначена
# 3. Прибыла на погрузку
# 4. Погружена
# 5. Транзит
# 6. Прибыла на выгрузку
# 7. Выгружена
# 8. Завершение рейса
# 9. На Т.О.
"""

print(menu)

input_user_change_status = input()

post(input_user_number_car, input_user_change_status)

get(input_user_number_car)
