import requests
# Имитация приложения водителя


# GET B777AG%2071
def get(number_car):
    url = f"http://127.0.0.1:5000/api/applications/{number_car}"  # кодирование пробела в URL
    response = requests.get(url)
    print(response.json())


# POST A080AA 71
def post(number_car):
    url = f"http://127.0.0.1:5000/api/applications/{number_car}"  # кодирование пробела в URL
    # JSON-тело запроса
    payload = {
        "new_status": "В пути"
    }

    # Отправка POST-запроса
    response = requests.post(url, json=payload)

    # Проверка статуса ответа
    if response.status_code == 200:
        print('Status updated successfully')
    else:
        print('Failed to update status:', response.text)


post("B777AG%2071")
post("A080AA%2071")


get("B777AG%2071")
get("A080AA%2071")
