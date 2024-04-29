# from POPF import get_price_fuel

platon_cost = 3.73
driver_salary = 12


def evaluation_of_effectiveness(autodor_price, fuel_price, kilometrs_for_platon, oll_kilometrs):
    result_cost = ((kilometrs_for_platon * platon_cost) + autodor_price + (driver_salary * oll_kilometrs)) + fuel_price

    return result_cost







