from sqlalchemy import create_engine, text

QUERY_FLIGHT_BY_ID = ("""
SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY 
FROM flights JOIN airlines ON flights.airline = airlines.id 
WHERE flights.ID = :id
;
""")
QUERY_FLIGHTS_BY_DATE = ("""
SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY 
FROM flights JOIN airlines ON flights.airline = airlines.id 
WHERE flights.DAY = :day 
  AND flights.MONTH= :month 
  AND flights.YEAR = :year
;
""")
QUERY_DELAYED_FLIGHTS_BY_AIRLINE = ("""
SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY 
FROM flights JOIN airlines ON flights.airline = airlines.id 
WHERE flights.DEPARTURE_DELAY >= 20 
  AND airlines.airline= :airline 
  AND flights.DEPARTURE_DELAY IS NOT NULL
  AND flights.DEPARTURE_DELAY  <> ''

;
""")
QUERY_DELAYED_FLIGHTS_BY_AIRPORT = ("""
SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY 
FROM flights JOIN airlines ON flights.airline = airlines.id 
             JOIN airports ON flights.ORIGIN_AIRPORT = airports.IATA_CODE 
WHERE flights.DEPARTURE_DELAY >= 20 
  AND  flights.DEPARTURE_DELAY  <> ''
  AND airports.IATA_CODE= :airport
;
""")
QUERY_ALL_AIRLINES = ("""
SELECT airlines.airline AS airline FROM airlines
;
""")
QUERY_NR_OF_DELAYED_FLIGHTS_BY_AIRLINE = ("""
SELECT COUNT(*) AS NR_of_delayed_flights 
FROM flights JOIN airlines ON flights.airline = airlines.id 
WHERE flights.DEPARTURE_DELAY >= 20 
  AND airlines.airline= :airline 
  AND flights.DEPARTURE_DELAY IS NOT NULL 
  AND  flights.DEPARTURE_DELAY  <> ''
;
""")
QUERY_NR_OF_FLIGHTS_BY_AIRLINE = ("""
SELECT COUNT(*) AS NR_of_flights 
FROM flights JOIN airlines ON flights.airline = airlines.id 
WHERE airlines.airline= :airline 
  AND flights.DEPARTURE_DELAY IS NOT NULL
  AND  flights.DEPARTURE_DELAY  <> ''
;
""")

QUERY_NR_OF_FLIGHTS_PER_HOUR_BY_DAY=("""
SELECT 
SUBSTR(departure_time, 1, 2) AS hour,
 COUNT(*) AS nr_of_flights
FROM flights
WHERE departure_time IS NOT NULL
  AND departure_time <> ''
GROUP BY SUBSTR(departure_time, 1, 2)
ORDER BY hour;
""")
QUERY_NR_OF_DELAYED_FLIGHTS_PER_HOUR_BY_DAY=("""
SELECT 
SUBSTR(departure_time, 1, 2) AS hour,
 COUNT(*) AS nr_of_flights
FROM flights
WHERE departure_time IS NOT NULL
  AND departure_time <> ''
  AND departure_delay >20
GROUP BY SUBSTR(departure_time, 1, 2)
ORDER BY hour;

""")

QUERY_ALL_IATA_CODES=("""
SELECT IATA_CODE FROM airports
;
"""
)

QUERY_DELAYED_PERCENTAGE_OF_FLIGHTS_BY_ORIG_AIRPORT_TO_DEST=("""
SELECT
    ORIGIN_AIRPORT,
    DESTINATION_AIRPORT,
    AVG(CASE WHEN DEPARTURE_DELAY > 20 THEN 1.0 ELSE 0.0 END) * 100 AS delay_percentage
FROM flights
GROUP BY ORIGIN_AIRPORT, DESTINATION_AIRPORT
HAVING COUNT(*) >= 20
ORDER BY ORIGIN_AIRPORT ASC;
"""
)
# Define the database URL
DATABASE_URL = "sqlite:///data/flights.sqlite3"

# Create the engine
engine = create_engine(DATABASE_URL)


def execute_query(query, params):
    """
    Execute an SQL query with the params provided in a dictionary,
    and returns a list of records (dictionary-like objects).
    If an exception was raised, print the error, and return an empty list.
    """
    try:
        with engine.connect() as conn:
            # your code here
            result = conn.execute(text(query),params)
            rows = result.fetchall()

    except Exception as e:
        print("Query error:", e)
        return []
    return rows


def get_flight_by_id(flight_id):
    """
    Searches for flight details using flight ID.
    If the flight was found, returns a list with a single record.
    """
    params = {'id': flight_id}
    return execute_query(QUERY_FLIGHT_BY_ID, params)

def get_flights_by_date(day, month, year):
    params = {'day': day, 'month': month, 'year': year}
    return execute_query(QUERY_FLIGHTS_BY_DATE, params)

def get_delayed_flights_by_airline(airline):
    params = {'airline': airline}
    return execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRLINE, params)

def get_delayed_flights_by_airport(airport):
    params = {'airport': airport}
    return execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRPORT, params)

def get_airlines()->list:
    params = {'airline': ""}
    return execute_query(QUERY_ALL_AIRLINES,params)

def get_nr_of_delayed_flights_by_airline(airline):
    params = {'airline': airline}
    return execute_query(QUERY_NR_OF_DELAYED_FLIGHTS_BY_AIRLINE, params)

def get_nr_of_flights_by_airline(airline):
    params = {'airline': airline}
    return execute_query(QUERY_NR_OF_FLIGHTS_BY_AIRLINE, params)

def get_number_of_flights_per_hour_of_day():
    params = {'day': ""}
    return execute_query(QUERY_NR_OF_FLIGHTS_PER_HOUR_BY_DAY, params)

def get_delayed_flights_per_hour_of_day():
    params = {'day': ""}
    return execute_query(QUERY_NR_OF_DELAYED_FLIGHTS_PER_HOUR_BY_DAY, params)

def get_all_iata_codes():
    params = {'airline': ""}
    return execute_query(QUERY_ALL_IATA_CODES, params)

def get_delayed_flights_by_airport():
    params = {'orig_airport': "" }
    return execute_query(QUERY_DELAYED_PERCENTAGE_OF_FLIGHTS_BY_ORIG_AIRPORT_TO_DEST, params)

