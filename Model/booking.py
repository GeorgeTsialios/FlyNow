class Booking:
    def __init__(self, booking_code, booking_date, total_price, main_passenger_ID):
        self.booking_code = booking_code
        self.booking_date = booking_date
        self.total_price = total_price
        self.main_passenger_ID = main_passenger_ID

    def addToTotalPrice(self, total_price):
        self.total_price += total_price