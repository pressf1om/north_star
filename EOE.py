# Импорт функции для получения цен на топливо
from POPF import get_price_fuel

# Словарь с расстояниями между городами
distances = {
    "Москва-Тверь": 162,
    "Тверь-Великий_Новгород": 299,
    "Великий_Новгород-Санкт-Петербург": 177
}


# Функция для расчета общего расстояния, которое можно проехать на имеющемся топливе
def how_much_kilometrs(available_fuel):
    # Бак 800 литров, расход 30 литров на 100 км
    total_kilometrs = (available_fuel * 100) / 30
    return total_kilometrs


# Функция для расчета стоимости маршрута
def calculate_route_cost(city_list, driver_salary, platon_cost, road_cost, kilometrs_for_platon, oll_kilometrs,
                         start_coordinates, available_fuel):
    # Получение отсортированного списка цен на топливо для городов
    sorted_fuel_price_list = sorted(get_price_fuel().items(), key=lambda x: x[1])

    # Определение, до какого города можно доехать на имеющемся топливе
    fuel_kilometrs = how_much_kilometrs(available_fuel)

    destination_city = None
    for city, price in sorted_fuel_price_list:
        # Проверяем, хватит ли топлива до следующего города в отсортированном списке
        if distances.get(city_list[-1] + "-" + city, float('inf')) <= fuel_kilometrs:
            destination_city = city
            break

    if destination_city:
        print(f"Можем доехать до {destination_city} на имеющемся топливе")

        # Определение выбранного маршрута
        chosen_route = city_list[-1] + "-" + destination_city
        print(f"Выбран маршрут: {chosen_route}")

        # Определение необходимости дозаправки
        fuel_needed = distances.get(chosen_route, float('inf')) / 100 * 30
        if fuel_needed > available_fuel:
            print("Требуется дозаправка.")

            # Определение города для дозаправки
            cheapest_refueling_city = None
            for city, price in sorted_fuel_price_list:
                if price < get_price_fuel().get(destination_city, [float('inf')])[0]:
                    cheapest_refueling_city = city
                    break
            if cheapest_refueling_city:
                print(f"Выбран город для дозаправки: {cheapest_refueling_city}")
                # Дополнительные расходы на топливо
                fuel_cost = distances.get(chosen_route, float('inf')) * price
                print(f"Стоимость дозаправки: {fuel_cost} руб.")
            else:
                print("Нет более дешевых городов для дозаправки.")
        else:
            print("Дозаправка не требуется.")
            # Расчет стоимости топлива
            fuel_cost = distances.get(chosen_route, float('inf')) * get_price_fuel().get(city_list[-1], float('inf'))[0]
            print(f"Стоимость топлива: {fuel_cost} руб.")

        # Расчет общей стоимости маршрута
        total_cost = kilometrs_for_platon * platon_cost + road_cost + oll_kilometrs * driver_salary + fuel_cost
        print(f"Общая стоимость маршрута: {total_cost} руб.")

    else:
        print("На имеющемся топливе не удастся доехать до самого дешевого города")


# Пример использования функции
calculate_route_cost(['Тверь', 'Великий Новгород'], 5.2, 3.73, 5000, 669, 720, None,
                     3000000000000000)  # Примерные значения топлива переданы для иллюстрации






