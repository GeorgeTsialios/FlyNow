class Passenger:
    def __init__(self, passenger_ID, first_name, last_name, age, phone_number, email, ageCategory=None, ageCategoryMaxAge=None):
        self.passenger_ID = passenger_ID
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.phone_number = phone_number
        self.email = email
        self.ageCategory = ageCategory
        self.ageCategoryMaxAge = ageCategoryMaxAge