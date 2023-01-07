class Airport:
    def __init__(self, airport_code, airport_name, country, city, location=None):
        self.airport_code = airport_code
        self.airport_name = airport_name
        self.country = country
        self.city = city
        self.location = location