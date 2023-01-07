import pytz

class Flight:
    def __init__(self, flight_number, departure_datetime, aircraft_type, departure_airport_code, arrival_datetime, arrival_airport_code, available_seats, duration, base_price, airline_ID, departure_airport_object, arrival_airport_object):
        self.flight_number = flight_number
        self.departure_datetime = departure_datetime
        self.aircraft_type = aircraft_type
        self.departure_airport_code = departure_airport_code
        self.arrival_datetime = arrival_datetime
        self.arrival_airport_code = arrival_airport_code
        self.available_seats = available_seats
        self.duration = duration
        self.base_price = base_price
        self.airline_ID = airline_ID
        self.departure_airport_object = departure_airport_object
        self.arrival_airport_object = arrival_airport_object

        self.setLocalTime()

    def setAirlineCode(self, airline_code):
        self.airline_code = airline_code
    
    def setPriceForPassengers(self, price):
        self.priceForPassengers = price

    def setLocalTime(self):
        self.departure_datetime_local = pytz.utc.normalize(pytz.utc.localize(self.departure_datetime)).astimezone(pytz.timezone(self.departure_airport_object.location.time_zone))
        self.arrival_datetime_local = pytz.utc.normalize(pytz.utc.localize(self.arrival_datetime)).astimezone(pytz.timezone(self.arrival_airport_object.location.time_zone))