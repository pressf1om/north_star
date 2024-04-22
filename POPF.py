import requests
from bs4 import BeautifulSoup


# Функция для удаления всех знаков после ценника
def strip_price(source):
    r_index = source.index('₽')
    s_price = source[:r_index].strip()
    return float(s_price)


def get_price_fuel():
    # Ссылка на веб-страницу с таблицей HTML
    url = 'https://fuelprices.ru/ceny-na-benzin-v-gorodah-rossii'

    # Отправляем GET-запрос к веб-сайту
    response = requests.get(url)

    # Переменные для хранения значений ячеек
    cities = []
    prices_list = []
    # Словарь
    prices = {}

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для парсинга HTML-кода
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все таблицы на веб-странице
        tables = soup.find_all('table')

        # Предположим, что нам нужна первая таблица на странице
        target_table = tables[0]

        # Получаем строки таблицы
        rows = target_table.find_all('tr')

        # Проходимся по каждой строке таблицы и извлекаем данные
        for row in rows:
            # Получаем ячейки (столбцы) в текущей строке
            cells = row.find_all('td')

            # Проверяем, что строка содержит данные
            if cells:
                # Извлекаем название города и цены
                city = cells[1].text.strip()
                # Добавляем название города в список 'cities'
                cities.append(city)
                # Извлекаем цены, но не добавляем их в список 'prices_list'
                city_prices = [strip_price(cell.text) for cell in cells[2:]]
                # Добавляем цены в список 'prices_list'
                prices_list.append(city_prices)
                # Превращаем все в словарь
                prices[city] = city_prices

    # Все значения списка
    # for _, (k, v) in enumerate(prices.items()):
    #    print(k, v)
    # Выводим ценники города(закоментить 'for', чтобы не вылезали все значения списка)
    # Дизель, аи-92, аи-95, аи-98
    return prices


# print(f"Дизель в городе Владимир: {get_price_fuel()['Владимир'][0]}")
# print(f"Дизель в городе Москва: {get_price_fuel()['Москва'][0]}")
# print(f"Дизель в городе Санкт-Петербург: {get_price_fuel()['Санкт-Петербург'][0]}")

