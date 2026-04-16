from importlib.metadata import pass_none

import flights_data as fd
from datetime import datetime
import sqlalchemy
# from pandas import DataFrame as df
import pandas as pd
import plot_flight_data as pfd

IATA_LENGTH = 3

def total_flights_per_airline(): """
    Calculates the total number of flights per airline
"""

def percentage_of_delayed_flights_per_airline():
# Algorithm:
# 1. Get all the airlines
# 2. Per airline get all the delayed flights (i.e. >= 20 minutes) without empty cells for DELAY
# 3. Per airline get the total number of flights, without empty cells for DELAY
# 4. Form a dict['airline', % delayed]
# 5. Plot the dict in a graph

    # Get all the airlines
    airlines=fd.get_airlines()
    delay_per_airline={}
    for airline in airlines:
        nr_of_flights_delayed=fd.get_nr_of_delayed_flights_by_airline(airline[0])
        total_nr_of_flights=fd.get_nr_of_flights_by_airline(airline[0])
        if float(total_nr_of_flights[0][0]) != 0: # Avoid a problem for a airline that's still without any flights
            delay_per_airline[airline[0]] = round((float(nr_of_flights_delayed[0][0]) / float(total_nr_of_flights[0][0]) * 100), 1)

    fig=pfd.plot_percentage_of_delayed_flights_per_airline(delay_per_airline)
    write_to_file = input("Would you like to export this data to a .png file? (y/n)")

    if write_to_file.lower() == "y" or write_to_file.lower() == "yes":
            f_name = input("Filename: ")
            fig.savefig(f_name + ".png")

def percentage_of_delayed_flights_per_hour_of_the_day():
    # Algorithm:
    # 1. get the number of flights per hour of the day
    # 2. get the number of delayed flights (i.e. >= 20 minutes) per hour of the day
    # 3. the received query output will be 2 lists with tuple containing
    #    (hour, #of total flights).
    #    (hour, #of delayed flights)
    # 4. create 1 list per hour of the day
    #    calculate the % of delayed flights [(hour,% of delayed flights)]
    # 4. Form a list['hour', % delayed]
    # 5. Plot the dict in a graph

    # get the number of flights per hour of the day
    total_flights_per_hour = fd.get_number_of_flights_per_hour_of_day()
    delayed_flights_per_hour = fd.get_delayed_flights_per_hour_of_day()
    percentage_of_delayed_flights_per_hour=[]
    hours_list=[]
    for hour in total_flights_per_hour:
        print(hour[0])
        delayed_flights_this_hour=delayed_flights_per_hour[int(hour[0])][1]
        total_flights_this_hour=total_flights_per_hour[int(hour[0])][1]
        percentage_of_delayed_flights_this_hour=(delayed_flights_this_hour/total_flights_this_hour)*100
        percentage_of_delayed_flights_per_hour.append(percentage_of_delayed_flights_this_hour)
        hours_list.append(int(hour[0]))
        # percentage_delayed_flights_ph=delayed_flights_per_hour[int(hour[0])][1])/delayed_flights_per_hour[hour[0][1]]
        # print(percentage_delayed_flights_ph)
        # percentage_of_delayed_flights_per_hour.append((hour[0], delayed_flights_per_hour[int(hour[0][1])]))
    print(percentage_of_delayed_flights_per_hour)
    print(hours_list)

    fig = pfd.plot_percentage_of_delayed_flight_per_hour(hours_list, percentage_of_delayed_flights_per_hour)
    write_to_file = input("Would you like to export this data to a .png file? (y/n)")

    if write_to_file.lower() == "y" or write_to_file.lower() == "yes":
        f_name = input("Filename: ")
        fig.savefig(f_name + ".png")





def delayed_flights_by_airline():
    """
    Asks the user for a textual airline name (any string will work here).
    Then runs the query using the data object method "get_delayed_flights_by_airline".
    When results are back, calls "print_results" to show them to on the screen.
    """
    airline_input = input("Enter airline name: ")
    results = fd.get_delayed_flights_by_airline(airline_input)
    print_results(results)

def delayed_flights_by_airport():
    """
    Asks the user for a textual IATA 3-letter airport code (loops until input is valid).
    Then runs the query using the data object method "get_delayed_flights_by_airport".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ")
        # Valide input
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    results = fd.get_delayed_flights_by_airport(airport_input)
    print_results(results)

def flight_by_id():
    """
    Asks the user for a numeric flight ID,
    Then runs the query using the data object method "get_flight_by_id".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        try:
            id_input = int(input("Enter flight ID: "))
        except Exception as e:
            print("Try again...")
        else:
            valid = True
    results = fd.get_flight_by_id(id_input)
    print_results(results)


def flights_by_date():
    """
    Asks the user for date input (and loops until it's valid),
    Then runs the query using the data object method "get_flights_by_date".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        try:
            date_input = input("Enter date in DD/MM/YYYY format: ")
            date = datetime.strptime(date_input, '%d/%m/%Y')
        except ValueError as e:
            print("Try again...", e)
        else:
            valid = True
    results = fd.get_flights_by_date(date.day, date.month, date.year)
    print_results(results)


def print_results(results):
    """
    Get a list of flight results (List of dictionary-like objects from SQLAachemy).
    Even if there is one result, it should be provided in a list.
    Each object *has* to contain the columns:
    FLIGHT_ID, ORIGIN_AIRPORT, DESTINATION_AIRPORT, AIRLINE, and DELAY.
    """
    data_export = []
    print(f"Got {len(results)} results.")
    for result in results:
        # turn result into dictionary
        result = result._mapping

        # Check that all required columns are in place
        try:
            delay = int(result['DELAY']) if result['DELAY'] else 0  # If delay columns is NULL, set it to 0
            origin = result['ORIGIN_AIRPORT']
            dest = result['DESTINATION_AIRPORT']
            airline = result['AIRLINE']
        except (ValueError, sqlalchemy.exc.SQLAlchemyError) as e:
            print("Error showing results: ", e)
            return

        # Different prints for delayed and non-delayed flights
        # Prepare data for storage  to a CSV file

        if delay and delay > 0:
            print(f"{result['ID']}. {origin} -> {dest} by {airline}, Delay: {delay} Minutes")
            data_export.append({'id': result['ID'], 'origin': dest, 'airline': airline, 'delay': str(delay) + "Minutes" })
        else:
            print(f"{result['ID']}. {origin} -> {dest} by {airline}")
            data_export.append({'id' : result['ID'], 'origin' : origin, 'dest':dest, 'airline' : airline})

    write_to_file=input("Would you like to export this data to a CSV file? (y/n)")

    if write_to_file.lower() == "y" or write_to_file.lower() == "yes":
        print(data_export)
        df = pd.DataFrame(data_export)
        f_name = input("Filename: ")
        df.to_csv(f_name, index=False)

def show_menu_and_get_input():
    """
    Show the menu and get user input.
    If it's a valid option, return a pointer to the function to execute.
    Otherwise, keep asking the user for input.
    """
    print("Menu:")
    for key, value in FUNCTIONS.items():
        print(f"{key}. {value[1]}")

    # Input loop
    while True:
        try:
            choice = int(input())
            if choice in FUNCTIONS:
                return FUNCTIONS[choice][0]
        except ValueError as e:
            pass
        print("Try again...")

"""
Function Dispatch Dictionary
"""
FUNCTIONS = { 1: (flight_by_id, "Show flight by ID"),
              2: (flights_by_date, "Show flights by date"),
              3: (delayed_flights_by_airline, "Delayed flights by airline"),
              4: (delayed_flights_by_airport, "Delayed flights by origin airport"),
              5: (percentage_of_delayed_flights_per_airline, "Graph of % of delayed flights per airline"),
              6: (percentage_of_delayed_flights_per_hour_of_the_day, "Graph of % of delayed flights per hour"),
              0: (quit, "Exit")
             }


def main():

    # The Main Menu loop
    while True:
        choice_func = show_menu_and_get_input()
        choice_func()


if __name__ == "__main__":
    main()