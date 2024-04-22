from POPF import get_price_fuel

fuel_price_list = {}


def evaluation_of_effectiveness(city_list, driver_salary, platon_cost, road_cost, kilometrs_for_platon, oll_kilometrs, available_fuel):
    for city_for_check in city_list:
        fuel_price_list[city_for_check] = [get_price_fuel()[f'{city_for_check}'][0]]
        # print(f"Дизель в городе {city_for_check}: {get_price_fuel()[f'{city_for_check}'][0]}")
        print(fuel_price_list[city_for_check])

    sorted_dictionary = dict(sorted(fuel_price_list.items(), key=lambda item: item[1]))
    print(sorted_dictionary)

    print(" ")
    print(f'Зарплата водителя за км: {driver_salary}')
    print(" ")
    print(f'Стоимость проезда платон за км: {platon_cost}')
    print(" ")
    print(f'Стоимость поездки по автодору: {road_cost}')

    result_cost = ((kilometrs_for_platon * platon_cost) + road_cost + (driver_salary * oll_kilometrs))

    return result_cost


print(f'Стоимость поездки: {evaluation_of_effectiveness(["Москва", "Тверь", "Великий Новгород"], 5.2, 3.73, 5000, 669, 720, 0)}')
print('+fuel cost')






