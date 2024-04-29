# from POPF import get_price_fuel


def evaluation_of_effectiveness(autodor_price, fuel_price, kilometrs_for_platon, oll_kilometrs, platon_cost, driver_salary):
    result_cost = ((kilometrs_for_platon * platon_cost) + autodor_price + (driver_salary * oll_kilometrs)) + fuel_price

    return result_cost







