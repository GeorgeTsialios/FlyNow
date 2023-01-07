from Model.location import Location
from Model.airport import Airport
from Model.airline import Airline
from Services.databaseService import DatabaseService
from Services.navigatorService import NavigatorService

class App:
    def __init__(self):
        self.databaseService = DatabaseService()

        self.populate_airlines()
        self.populate_locations()
        self.populate_airports()

        self.navigator = NavigatorService(self)

    def populate_airlines(self):
        airline_data = self.databaseService.select("""
            SELECT *
            FROM AIRLINE;
        """)

        self.airlines = []

        for row in airline_data:
            self.airlines.append(
                Airline(
                    airline_ID = row[0],
                    airline_name = row[1]
                )
            )

    def populate_locations(self):
        location_data = self.databaseService.select("""
            SELECT *
            FROM LOCATION;
        """)

        self.locations = []

        for row in location_data:
            self.locations.append(
                Location(
                    country = row[0],
                    city = row[1],
                    region = row[2],
                    time_zone = row[3]
                )
            )

        self.cities = sorted(set([location.city for location in self.locations]))
        self.countries = sorted(set([location.country for location in self.locations]))
        self.regions = sorted(set([location.region for location in self.locations]))

    def populate_airports(self):
        airport_data = self.databaseService.select("""
            SELECT *
            FROM AIRPORT;
        """)

        self.airports = []

        for row in airport_data:
            self.airports.append(
                Airport(
                    airport_code = row[0],
                    airport_name = row[1],
                    country = row[2],
                    city = row[3],
                    location = next(item for item in self.locations if item.country == row[2] and item.city == row[3])
                )
            )


def main():
    print("------------------------------------------")
    print("            WELCOME TO FlyNow!            ")
    print("------------------------------------------")

    app = App()

    app.databaseService.close()



if __name__ == "__main__":
    main()