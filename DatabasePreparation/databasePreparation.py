from Model.aircraft import Aircraft
from Model.seatmap import Seatmap
from Model.location import Location
from Model.airport import Airport
from Model.airline import Airline
from Model.flight import Flight
from Model.agepolicy import AgePolicy
from Model.fare import Fare
from Model.luggagetype import LuggageType

import sqlite3
import json
from datetime import datetime, timedelta
import pytz
import random

class DatabasePreparator:
    def __init__(self):
        self.openDatabase()
        print('db opened')
        self.prepareAircraftAndSeatmapTables()
        print('aircraft and seatmap ready')
        self.prepareTakenSeatTable()
        print('taken seat ready')
        self.preparePassengerTable()
        print('passenger ready')
        self.prepareAirportAndLocationTables()
        print('airport and location ready')
        self.prepareAirlineTable()
        print('airline ready')
        self.prepareFlightTable()
        print('flight ready')
        self.prepareTicketTable()
        print('ticket ready')
        self.prepareBookingTable()
        print('booking ready')
        self.prepareAgePolicyTable()
        print('age policy ready')
        self.prepareFareTable()
        print('fare ready')
        self.prepareLuggageTypeTable()
        print('luggage type ready')
        self.prepareLuggageTable()
        print('luggage ready')

        self.conn.close()

    def openDatabase(self):
        self.conn = sqlite3.connect("Database\\FlyNowDatabase.db")
        self.conn.execute("PRAGMA foreign_keys=ON;")

    def prepareAircraftAndSeatmapTables(self):
        aircraftsSeatmapData = json.load(open('JSONfiles\\aircrafts_seats.json'))

        aircrafts = []
        seatmap = []

        for datum in aircraftsSeatmapData:
            aircraft_type = datum['aircraft_type'].upper()

            aircrafts.append(Aircraft(
                aircraft_type
            ))

            seatmapData = datum['seats']
            
            for seatmapDatum in seatmapData:
                seat_number = seatmapDatum[0].zfill(3)
                seat_class = seatmapDatum[1]

                seatmap.append(Seatmap(
                    aircraft_type,
                    seat_number,
                    seat_class
                ))

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "AIRCRAFT"
            (
                "aircraft_type"		varchar(30)		NOT NULL,

                PRIMARY KEY("aircraft_type")
            );
        """)

        for aircraft in aircrafts:
            try:
                self.conn.execute(f"""
                    INSERT INTO "AIRCRAFT" VALUES
                    ("{aircraft.aircraft_type}");
                """)
            except Exception:
                print(aircraft.aircraft_type)
                raise

        self.conn.commit()

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "SEAT_MAP"
            (
                "aircraft_type"		varchar(30)		NOT NULL,
                "seat_number"		varchar(4)		NOT NULL,
                "seat_class"		varchar(30)		DEFAULT 'ECONOMY',

                PRIMARY KEY("aircraft_type","seat_number"),
                FOREIGN KEY ("aircraft_type") REFERENCES "AIRCRAFT"("aircraft_type") ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)

        for seat in seatmap:
            try:
                self.conn.execute(f"""
                    INSERT INTO "SEAT_MAP" VALUES
                    ("{seat.aircraft_type}", "{seat.seat_number}", "{seat.seat_class}");
                """)
            except Exception:
                print(seat.aircraft_type, seat.seat_number)
                raise

        self.conn.commit()

    def prepareTakenSeatTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "TAKEN_SEAT"
            (
                "seat_number"		varchar(4)		NOT NULL,
                "flight_number"		varchar(10)		NOT NULL,
                "departure_datetime"	datetime		NOT NULL,

                PRIMARY KEY ("seat_number","flight_number","departure_datetime"),
                FOREIGN KEY ("flight_number","departure_datetime") REFERENCES "FLIGHT"("flight_number","departure_datetime") ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS "idx_TAKEN_SEAT" ON "TAKEN_SEAT"(flight_number);	
        """)

        self.conn.commit()

    def preparePassengerTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "PASSENGER"
            (
                "passenger_ID"	varchar(30)		NOT NULL,
                "first_name"	varchar(30)		NOT NULL,
                "last_name"		varchar(30)		NOT NULL,
                "age"			smallint		NOT NULL,
                "phone_number"	varchar(20)		DEFAULT '',
                "email"		varchar(60),

                PRIMARY KEY ("passenger_ID"),
                CONSTRAINT "Valid_Age" CHECK ("age" >= 0)
            );
        """)

        self.conn.commit()

    def prepareAirportAndLocationTables(self):
        airportsData = json.load(open('JSONfiles\\airports_from_flightlabs.json'))
        citiesData = json.load(open('JSONfiles\\cities_from_airlabs.json'))
        countriesData = json.load(open('JSONfiles\\countries_from_restcountries.json', encoding='utf-8'))

        airports = []
        locations = []

        for datum in airportsData:
            if "Rail" in datum['nameAirport'] or "Bus Station" in datum['nameAirport']:
                continue
            
            try:
                city = next(city for city in citiesData if city['city_code'] == datum['codeIataCity'])
            except StopIteration: # the city where the airport is located cannot be found. Discard.
                continue
            country = next(country for country in countriesData if country['cca2'] == city['country_code'])
            if datum['timezone'] is None or '+' in datum['timezone']:
                continue

            try:
                location = next(item for item in locations if item.city == city['name'] and item.country == country['name']['common'])
            except StopIteration:
                try:
                    locations.append(Location(
                        country['name']['common'],
                        city['name'],
                        country['subregion'],
                        datum['timezone']
                    ))
                except KeyError: # Antarctica doesn't have subregions. Replace subregion with region ('Antarctic').
                    locations.append(Location(
                        country['name']['common'],
                        city['name'],
                        country['region'],
                        datum['timezone']
                    ))

            airports.append(Airport(
                datum['codeIataAirport'],
                datum['nameAirport'],
                country['name']['common'],
                city['name']
            ))

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "AIRPORT"
            (
                "airport_code"	char(3)		NOT NULL,
                "airport_name"	varchar(100)	DEFAULT '',
                "country"		varchar(30)		DEFAULT '',
                "city"		varchar(30)		DEFAULT '',
                
                PRIMARY KEY ("airport_code"),
                FOREIGN KEY ("country","city") REFERENCES "LOCATION"("country","city") ON DELETE SET DEFAULT ON UPDATE CASCADE,
                CONSTRAINT "Valid_Airport_code" CHECK(length("airport_code") = 3)
            );
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "LOCATION"
            (
                "country"		varchar(30)		NOT NULL,
                "city"		varchar(30)		NOT NULL,
                "region"		varchar(30)		DEFAULT '',
                "time_zone"		varchar(50)		DEFAULT '',
                
                PRIMARY KEY ("country","city")
            );
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS "idx_AIRPORT" ON "AIRPORT"(city);
        """)

        for location in locations:
            try:
                self.conn.execute(f"""
                    INSERT INTO "LOCATION" VALUES
                    ("{location.country}", "{location.city}", "{location.region}", "{location.time_zone}");
                """)
            except Exception:
                print(location.country, location.city)
                raise

        for airport in airports:
            self.conn.execute(f"""
                INSERT INTO "AIRPORT" VALUES
                ("{airport.airport_code}", "{airport.airport_name}", "{airport.country}", "{airport.city}");
            """)

        self.conn.commit()

    def prepareAirlineTable(self):
        airlinesData = json.load(open('JSONfiles\\airlines_from_flightlabs.json'))

        airlines = []

        for datum in airlinesData:
            if datum['statusAirline'] != "active":
                continue
            if datum['codeIcaoAirline'] == "":
                continue
            airlines.append(Airline(
                datum['codeIcaoAirline'],
                datum['nameAirline']
            ))

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "AIRLINE"
            (
                "airline_ID"	char(3)		NOT NULL,
                "airline_name"	varchar(30)		DEFAULT '',

                PRIMARY KEY ("airline_ID")
                CONSTRAINT "Valid_Airline_ID" CHECK (length("airline_ID") = 3)
            );
        """)

        for airline in airlines:
            try:
                self.conn.execute(f"""
                    INSERT INTO "AIRLINE" VALUES
                    ("{airline.airline_ID}", "{airline.airline_name}");
                """)
            except sqlite3.IntegrityError:
                continue
            except Exception:
                print(airline.airline_name)
                raise

        self.conn.commit()

    def prepareFlightTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "FLIGHT"
            (
                "flight_number"			varchar(10)		NOT NULL,
                "departure_datetime"		datetime		NOT NULL,
                "departure_airport_code"	char(3)		NOT NULL,
                "arrival_datetime"		datetime		NOT NULL,
                "arrival_airport_code"		char(3)		NOT NULL,
                "aircraft_type"			varchar(20)		DEFAULT '',
                "available_seats"			smallint		DEFAULT '100',
                "duration"				numeric		GENERATED ALWAYS AS (ROUND(((julianday("arrival_datetime") - julianday("departure_datetime")) * 24 * 60),2)),
                "base_price"			integer		NOT NULL,
                "airline_ID"			char(3)		NOT NULL,
                
                PRIMARY KEY ("flight_number","departure_datetime"),
                FOREIGN KEY ("departure_airport_code") REFERENCES "AIRPORT"("airport_code") ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY ("arrival_airport_code") REFERENCES "AIRPORT"("airport_code") ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY ("aircraft_type") REFERENCES "AIRCRAFT"("aircraft_type") ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY ("airline_ID") REFERENCES "AIRLINE"("airline_ID") ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT "Valid_Datetimes" CHECK ("arrival_datetime" > "departure_datetime"),
                CONSTRAINT "Valid_Base_Price" CHECK ("base_price" > 0)
            );
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS "idx_FLIGHT" ON "FLIGHT"(departure_airport_code);
        """)

        airports = [
            'ATH', 'BCN', 'CDG',
            'BER', 'HEL', 'HKG',
            'DXB', 'DOH', 'AUH',
            'HND', 'ZRH', 'ICN',
            'SIN', 'IST', 'AMS',
            'VIE', 'LHR', 'MUC',
            'MXP', 'LGW', 'JFK'
        ]

        allLocations = []
        c = self.conn.cursor()
        c.execute(f"""
            SELECT *
            FROM LOCATION;
        """)
        allLocationData = c.fetchall()
        for allLocationDatum in allLocationData:
            allLocations.append(Location(
                allLocationDatum[0],
                allLocationDatum[1],
                allLocationDatum[2],
                allLocationDatum[3]
            ))

        allAirports = []
        c = self.conn.cursor()
        c.execute(f"""
            SELECT *
            FROM AIRPORT;
        """)
        allAirportData = c.fetchall()
        for allAirportDatum in allAirportData:
            allAirports.append(Airport(
                allAirportDatum[0],
                allAirportDatum[1],
                allAirportDatum[2],
                allAirportDatum[3],
                location = next(item for item in allLocations if item.country == allAirportDatum[2] and item.city == allAirportDatum[3])
            ))

        allAirlines = []
        c = self.conn.cursor()
        c.execute(f"""
            SELECT *
            FROM AIRLINE;
        """)
        allAirlineData = c.fetchall()
        for allAirlineDatum in allAirlineData:
            allAirlines.append(Airline(
                allAirlineDatum[0],
                allAirlineDatum[1]
            ))

        flights = []

        faulty_flight_records = 0
        total_flight_records = 0

        for airport in airports:
            for day in range(1, 32):
                print(airport, day, faulty_flight_records, total_flight_records)
                flightsData = json.load(open(f'JSONfiles\\flights_{airport}_2023-03\\future_flights_from_flightlabs_{airport}_{datetime(2023, 3, day).strftime("%Y-%m-%d")}.json', encoding='utf-8'))
                total_flight_records += len(flightsData)

                for datum in flightsData:
                    try:
                        if 'codeshared' in datum:
                            continue

                        if datum['departure']['scheduledTime'] == '' or datum['arrival']['scheduledTime'] == '' or datum['aircraft']['modelCode'] == '':
                            faulty_flight_records += 1
                            continue

                        if datum['flight']['iataNumber'] != '':
                            flight_number = datum['flight']['iataNumber'].upper()
                        else:
                            flight_number = datum['flight']['icaoNumber'].upper()

                        departure_airport_code = datum['departure']['iataCode'].upper()
                        departure_airport_object = next(item for item in allAirports if item.airport_code == departure_airport_code)
                        departure_datetime_local = datetime(2023, 3, day, int(datum['departure']['scheduledTime'].split(':')[0]), int(datum['departure']['scheduledTime'].split(':')[1]))
                        departure_datetime_utc = pytz.timezone(departure_airport_object.location.time_zone).normalize(pytz.timezone(departure_airport_object.location.time_zone).localize(departure_datetime_local)).astimezone(pytz.utc)

                        aircraft_type = datum['aircraft']['modelCode'].upper()

                        arrival_airport_code = datum['arrival']['iataCode'].upper()
                        if arrival_airport_code == 'DIA':
                            arrival_airport_code = 'DOH'
                        arrival_airport_object = next(item for item in allAirports if item.airport_code == arrival_airport_code)
                        arrival_datetime_local = datetime(2023, 3, day, int(datum['arrival']['scheduledTime'].split(':')[0]), int(datum['arrival']['scheduledTime'].split(':')[1]))
                        arrival_datetime_utc = pytz.timezone(arrival_airport_object.location.time_zone).normalize(pytz.timezone(arrival_airport_object.location.time_zone).localize(arrival_datetime_local)).astimezone(pytz.utc)

                        if departure_datetime_utc == arrival_datetime_utc:
                            faulty_flight_records += 1
                            continue

                        # Handle day changes
                        if arrival_datetime_utc < departure_datetime_utc: # arrives next day (after midnight). Add a day.
                            arrival_datetime_utc += timedelta(days=1)
                            if departure_airport_code == 'JFK' and arrival_datetime_utc < departure_datetime_utc and departure_datetime_utc > datetime(departure_datetime_local.year, departure_datetime_local.month, departure_datetime_local.day, 12, tzinfo=pytz.utc): # happens for JFK-SIN flights. Add two days.
                                arrival_datetime_utc += timedelta(days=2)
                        if (arrival_datetime_utc - departure_datetime_utc).days > 0:
                            arrival_datetime_utc -= timedelta(days=1)

                        # Handle DST changes
                        if departure_airport_code == 'IST' and departure_datetime_utc > datetime(2023, 3, 26, 3, tzinfo=pytz.utc):
                            departure_datetime_utc -= timedelta(hours=1)
                        if arrival_airport_code == 'IST' and arrival_datetime_utc > datetime(2023, 3, 26, tzinfo=pytz.utc):
                            arrival_datetime_utc -= timedelta(hours=1)

                        # Determine available seats based on aircraft type.
                        c = self.conn.cursor()
                        c.execute(f"""
                            SELECT COUNT(*)
                            FROM SEAT_MAP
                            WHERE aircraft_type = "{aircraft_type}";
                        """)
                        response = c.fetchall()
                        if len(response) != 1:
                            raise ValueError
                        available_seats = response[0][0]

                        duration = int((arrival_datetime_utc - departure_datetime_utc).seconds / 60)
                        
                        # Base price calculation algorithm
                        # We assume that the cost of a flight/minute is 0.68€. We multiply this value by the duration of the flight.
                        # We multiply by a random coefficient between [0.8, 1.2] to represent the variation of the cost of each flight/airline.
                        
                        base_price = round(random.uniform(0.8, 1.2) * 0.68 * duration, 2)
                        airline_ID = datum['airline']['icaoCode'].upper()

                        try:
                            airline_object = next(item for item in allAirlines if item.airline_ID == airline_ID)
                        except StopIteration:
                            faulty_flight_records += 1
                            continue
                        
                        flights.append(Flight(
                            flight_number,
                            departure_datetime_utc,
                            aircraft_type,
                            departure_airport_code,
                            arrival_datetime_utc,
                            arrival_airport_code,
                            available_seats,
                            duration,
                            base_price,
                            airline_ID,
                            None,
                            None
                        ))
                    except Exception:
                        print(datum)
                        raise
                
        for flight in flights:
            try:
                self.conn.execute(f"""
                    INSERT INTO "FLIGHT"("flight_number","departure_datetime","aircraft_type","departure_airport_code","arrival_datetime","arrival_airport_code","available_seats","base_price","airline_ID") VALUES
                    ("{flight.flight_number}", "{str(flight.departure_datetime).split('+')[0]}", "{flight.aircraft_type}", "{flight.departure_airport_code}", "{str(flight.arrival_datetime).split('+')[0]}", "{flight.arrival_airport_code}", "{flight.available_seats}", "{flight.base_price}", "{flight.airline_ID}");
                """)
            except Exception:
                print(
                    flight.flight_number,
                    flight.departure_datetime,
                    flight.aircraft_type,
                    flight.departure_airport_code,
                    flight.arrival_datetime,
                    flight.arrival_airport_code,
                    flight.available_seats,
                    flight.duration,
                    flight.base_price,
                    flight.airline_ID
                )
                raise

        self.conn.commit()

    def prepareTicketTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "TICKET"
            (
                "ticket_ID"			varchar(22)		NOT NULL,
                "price"			decimal(6,2)	NOT NULL,
                "seat_number"		varchar(4)		NOT NULL,
                "flight_number"		varchar(10)		NOT NULL,
                "departure_datetime"	datetime		NOT NULL,
                "passenger_ID"		varchar(20)		NOT NULL,
                "booking_code"		varchar(20)		NOT NULL,
                "fare_name"			varchar(30)		NOT NULL,
                "airline_ID"		char(3)		NOT NULL,

                PRIMARY KEY	("ticket_ID"),
                FOREIGN KEY ("passenger_ID")	REFERENCES "PASSENGER"("passenger_ID") ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY ("seat_number","flight_number","departure_datetime")	REFERENCES "TAKEN_SEAT"("seat_number","flight_number","departure_datetime") ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY ("booking_code")	REFERENCES "BOOKING"("booking_code") ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY ("fare_name","airline_ID")	REFERENCES "FARE"("fare_name","airline_ID") ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT "Valid_Price" CHECK ("price" > 0)	
            );
        """)

        self.conn.commit()

    def prepareBookingTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "BOOKING"
            (
                "booking_code"		varchar(20)		NOT NULL,
                "booking_date"		date			DEFAULT NULL,
                "total_price"		decimal(8,2)	NOT NULL,
                "main_passenger_ID"	varchar(20)		NOT NULL	DEFAULT '0',

                PRIMARY KEY ("booking_code"),
                FOREIGN KEY ("main_passenger_ID") REFERENCES "PASSENGER"("passenger_ID") ON DELETE SET DEFAULT ON UPDATE CASCADE
            );
        """)

        self.conn.commit()

    def prepareAgePolicyTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "AGE_POLICY"
            (
                "airline_ID"			char(3)		NOT NULL,
                "max_age"				smallint		NOT NULL,
                "age_price_coefficient"		decimal(3,2)	DEFAULT '1',

                PRIMARY KEY ("airline_ID", "max_age"),
                FOREIGN KEY ("airline_ID") REFERENCES "AIRLINE"("airline_ID") ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT "Valid_Max_Age" CHECK("max_age" > 0)
            );
        """)

        agePoliciesData = json.load(open('JSONfiles\\agePolicies.json'))

        agePolicies = []

        for datum in agePoliciesData:
            agePolicies.append(AgePolicy(
                datum['airline_ID'],
                datum['max_age'],
                datum['age_price_coefficient']
            ))

        for agePolicy in agePolicies:
            try:
                self.conn.execute(f"""
                    INSERT INTO "AGE_POLICY" VALUES
                    ("{agePolicy.airline_ID}", "{agePolicy.max_age}", "{agePolicy.age_price_coefficient}");
                """)
            except Exception:
                print(agePolicy.airline_ID, agePolicy.max_age)

        self.conn.commit()

    def prepareFareTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "FARE"
            (
                "fare_name"				varchar(30)		NOT NULL,
                "airline_ID"			char(3)		NOT NULL,
                "amenities"				varchar(100)	DEFAULT '',
                "fare_price_coefficient"	decimal(3,2)	DEFAULT '1',

                PRIMARY KEY("fare_name","airline_ID"),
                FOREIGN KEY ("airline_ID") REFERENCES "AIRLINE"("airline_ID") ON DELETE CASCADE ON UPDATE CASCADE		
            );
        """)

        faresData = json.load(open('JSONfiles\\fares.json'))

        fares = []

        for datum in faresData:
            fares.append(Fare(
                datum['fare_name'],
                datum['airline_ID'],
                datum['amenities'],
                datum['fare_price_coefficient']
            ))

        for fare in fares:
            try:
                self.conn.execute(f"""
                    INSERT INTO "FARE" VALUES
                    ("{fare.fare_name}", "{fare.airline_ID}", "{fare.amenities}", "{fare.fare_price_coefficient}");
                """)
            except Exception:
                print(fare.fare_name, fare.airline_ID)
                raise

        self.conn.commit()

    def prepareLuggageTypeTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "LUGGAGE_TYPE"
            (
                "airline_ID"	char(3)		NOT NULL,
                "weight"		smallint		NOT NULL,
                "cost"		smallint		NOT NULL,
                "category"		varchar(20)		DEFAULT 'Checked',

                PRIMARY KEY("airline_ID","weight"),
                FOREIGN KEY ("airline_ID") REFERENCES "AIRLINE"("airline_ID") ON DELETE CASCADE ON UPDATE CASCADE	
                CONSTRAINT "Valid_Cost" CHECK ("cost" >= 0),
                CONSTRAINT "Valid_Weight" CHECK ("weight" >= 0),
                CONSTRAINT "Valid_Category" CHECK ("category" = 'Checked' OR "category" = 'Carry-on')
            );
        """)

        luggageTypesData = json.load(open('JSONfiles\\luggageTypes.json'))

        luggageTypes = []

        for datum in luggageTypesData:
            luggageTypes.append(LuggageType(
                datum['airline_ID'],
                datum['weight'],
                datum['cost'],
                datum['category']
            ))

        for luggageType in luggageTypes:
            try:
                self.conn.execute(f"""
                    INSERT INTO "LUGGAGE_TYPE" VALUES
                    ("{luggageType.airline_ID}", "{luggageType.weight}", "{luggageType.cost}", "{luggageType.category}");
                """)
            except Exception:
                print(luggageType.airline_ID, luggageType.weight)
                raise

        self.conn.commit()

    def prepareLuggageTable(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS "LUGGAGE"
            (
                "luggage_ID"	varchar(23)		NOT NULL,
                "ticket_ID"		varchar(20)		NOT NULL,
                "airline_ID"	char(3)		NOT NULL,
                "weight"		smallint		NOT NULL,

                PRIMARY KEY("luggage_ID")
                FOREIGN KEY("ticket_ID") REFERENCES "TICKET"("ticket_ID")	ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY ("airline_ID","weight") REFERENCES "LUGGAGE_TYPE"("airline_ID","weight") ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)

        self.conn.commit()







