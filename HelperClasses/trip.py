# import pytz

class Trip:
    def __init__(self):
        self.flights = []
        self.airports = []
    
    def addFlight(self, flight):
        self.flights.append(flight)
    
    def addAirport(self, airport):
        self.airports.append(airport)
    
    def setTotalDuration(self, totalDuration):
        self.totalDuration = totalDuration
    
    def setTotalPrice(self, totalPrice):
        self.totalPrice = totalPrice
    
    def display(self, index, total):
        print(f'{index:2d}.', end='\t')

        print(self.flights[0].departure_airport_code, end=' ')
        # departure_datetime_local = pytz.utc.normalize(pytz.utc.localize(self.flights[0].departure_datetime)).astimezone(pytz.timezone(self.airports[0].location.time_zone))
        print(self.flights[0].departure_datetime_local.strftime('%Y-%m-%d %H:%M'), end=' > ')
        # arrival_datetime_local = pytz.utc.normalize(pytz.utc.localize(self.flights[-1].arrival_datetime)).astimezone(pytz.timezone(self.airports[1].location.time_zone))
        print(self.flights[-1].arrival_datetime_local.strftime('%Y-%m-%d %H:%M'), end=' ')
        print(self.flights[-1].arrival_airport_code, end=' -- ')
        print(f'{self.totalPrice:.2f}€', end='')

        available_seats = min([x.available_seats for x in self.flights])

        if available_seats < 10:
            print(f'-- Only {available_seats} seats left!')
        else:
            print()

        if len(self.flights) == 1:
            print(f'\tDirect ({self.totalDuration // 60}h {self.totalDuration % 60:02d}min) - Operated by {self.flights[0].airline_ID}')
        elif len(self.flights) == 2:
            print(f'\t1 stop in {self.flights[0].arrival_airport_code} ({self.totalDuration // 60}h {self.totalDuration % 60:02d}min) - Operated by {" and ".join(set([flight.airline_ID for flight in self.flights]))}')
        else:
            print(f'\t2 stops in {self.flights[0].arrival_airport_code} and {self.flights[1].arrival_airport_code} ({self.totalDuration // 60}h {self.totalDuration % 60:02d}min) - Operated by {" and ".join(set([flight.airline_ID for flight in self.flights]))}')
        print(f'\t({", ".join([flight.flight_number for flight in self.flights])})')
        print()
