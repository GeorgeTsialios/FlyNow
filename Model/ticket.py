class Ticket:
    def __init__(self, ticket_ID, price, seat_number, flight_number, departure_datetime, passenger_ID, booking_code, fare_name, airline_ID):
        self.ticket_ID = ticket_ID
        self.price = price
        self.seat_number = seat_number
        self.flight_number = flight_number
        self.departure_datetime = departure_datetime
        self.passenger_ID = passenger_ID
        self.booking_code = booking_code
        self.fare_name = fare_name
        self.airline_ID = airline_ID