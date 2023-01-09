import sqlite3
import sys

class DatabaseService:
    def __init__(self):
        self.conn = sqlite3.connect('Database\\FlyNowDatabase.db')
        self.conn.execute("PRAGMA foreign_keys=ON")

    def close(self):
        self.conn.close()
    
    def select(self, query):
        c = self.conn.cursor()
        c.execute(query)
        data = c.fetchall()
        return data
    
    def searchTripsZeroStops(self, departureCity, passengersAdultsAndChildren, arrivalCity=None, arrivalCountry=None, arrivalRegion=None, departureDate=None, travelMonth=None, airline_name=None, base_price=None, referenceDate=None):
        try:
            assert (not arrivalCity is None) or (not arrivalCountry is None) or (not arrivalRegion is None)
            assert (not departureDate is None) or (not travelMonth is None)
        except AssertionError:
            print("A critical internal error occurred. Please refer to the developers, mentioning the error code \"searchTripsZeroStopsAssertionError\". Terminating...")
            sys.exit(-1)
        
        query = f"""
            SELECT 
                flight_number,
                departure_airport_code,
                DEPARTURE_AIRPORT.city AS departure_city,
                departure_datetime,
                arrival_airport_code,
                ARRIVAL_AIRPORT.city AS arrival_city,
                arrival_datetime,
                available_seats,
                airline_name,
                    duration AS duration_MIN,
                base_price
        """

        if not travelMonth is None and not referenceDate is None:
            query += f""",
                julianday(strftime('%Y-%m-%d', departure_datetime) || ' 15:00:00') - julianday(strftime('%Y-%m-%d', '{str(referenceDate)}') || ' 15:00:00') AS days
            """

        if arrivalRegion is None:
            query += f"""
                FROM 			
                                (		
                                        (
                                        FLIGHT JOIN AIRPORT AS DEPARTURE_AIRPORT ON departure_airport_code = DEPARTURE_AIRPORT.airport_code
                                        ) 
                                JOIN AIRPORT AS ARRIVAL_AIRPORT ON arrival_airport_code = ARRIVAL_AIRPORT.airport_code
                                ) 
                    NATURAL JOIN AIRLINE

                WHERE  
                    DEPARTURE_AIRPORT.city = '{departureCity}' 			 AND 
                    available_seats >= {passengersAdultsAndChildren}
            """

            if not arrivalCity is None:
                query += f""" AND ARRIVAL_AIRPORT.city = '{arrivalCity}'"""
            else:
                query += f""" AND ARRIVAL_AIRPORT.country = '{arrivalCountry}'"""
        
        else:
            query += f"""
                FROM 			
                        (
                                (		
                                        (
                                        FLIGHT JOIN AIRPORT AS DEPARTURE_AIRPORT ON departure_airport_code = DEPARTURE_AIRPORT.airport_code
                                        ) 
                                JOIN AIRPORT AS ARRIVAL_AIRPORT ON arrival_airport_code = ARRIVAL_AIRPORT.airport_code
                                ) 
                        NATURAL JOIN AIRLINE
                        )
                    JOIN LOCATION ON (ARRIVAL_AIRPORT.city = LOCATION.city AND ARRIVAL_AIRPORT.country = LOCATION.country)

                WHERE 
                    DEPARTURE_AIRPORT.city = '{departureCity}' 			 AND 
                    available_seats >= {passengersAdultsAndChildren}     AND
                    region = '{arrivalRegion}'
            """

        if not departureDate is None:
            query += f""" AND departure_datetime LIKE '{departureDate.strftime('%Y-%m-%d')} __:__:__'"""
        else:
            query += f""" AND departure_datetime LIKE '{travelMonth.strftime('%Y-%m')}-__ __:__:__'"""

        if not airline_name is None:
            query += f""" AND airline_name = '{airline_name}'"""
        if not base_price is None:
            query += f""" AND base_price < {base_price}"""

        if not travelMonth is None and not referenceDate is None:
            query += f""" AND (julianday(strftime('%Y-%m-%d', departure_datetime) || ' 15:00:00') - julianday(strftime('%Y-%m-%d', '{str(referenceDate)}') || ' 15:00:00')) BETWEEN 1 AND 5
                        AND (julianday(departure_datetime) - julianday('{str(referenceDate)}')) >= 0.5
            
                ORDER BY days DESC, base_price,departure_datetime;"""
        else:
            query += """ ORDER BY base_price,departure_datetime;"""
        return self.select(query)
    
    def searchTripsOneStop(self, departureCity, passengersAdultsAndChildren, arrivalCity=None, arrivalCountry=None, arrivalRegion=None, departureDate=None, travelMonth=None, airline_name=None, base_price=None, referenceDate=None):
        try:
            assert (not arrivalCity is None) or (not arrivalCountry is None) or (not arrivalRegion is None)
            assert (not departureDate is None) or (not travelMonth is None)
        except AssertionError:
            print("A critical internal error occurred. Please refer to the developers, mentioning the error code \"searchTripsOneStopAssertionError\". Terminating...")
            sys.exit(-1)

        query = f"""
            SELECT 
                FLIGHT_1.flight_number AS flight_1_number, 
                FLIGHT_1.departure_airport_code,
                DEPARTURE_AIRPORT.city AS departure_city,
                FLIGHT_1.departure_datetime AS flight_1_departure_datetime,
                FLIGHT_1.arrival_airport_code AS intermediate_airport_code,
                INTERMEDIATE_AIRPORT.city AS intermediate_city,
                FLIGHT_1.arrival_datetime AS flight_1_arrival_datetime,
                FLIGHT_1.available_seats AS flight_1_available_seats,
                AIRLINE_1.airline_name AS flight_1_airline_name,
                FLIGHT_1.base_price AS flight_1_base_price,

                FLIGHT_2.flight_number AS flight_2_number,
                FLIGHT_2.departure_airport_code AS intermediate_airport_code,
                INTERMEDIATE_AIRPORT.city AS intermediate_city,
                FLIGHT_2.departure_datetime AS flight_2_departure_datetime, 
                FLIGHT_2.arrival_airport_code,
                ARRIVAL_AIRPORT.city AS arrival_city,
                FLIGHT_2.arrival_datetime AS flight_2_arrival_datetime,
                FLIGHT_2.available_seats AS flight_2_available_seats,
                AIRLINE_2.airline_name AS flight_2_airline_name,
                FLIGHT_2.base_price AS flight_2_base_price,

                ROUND(((julianday(FLIGHT_2.arrival_datetime) - julianday(FLIGHT_1.departure_datetime)) * 24), 2) AS total_duration_HOURS, 
                FLIGHT_1.base_price + FLIGHT_2.base_price AS Total_price
        """

        if not travelMonth is None and not referenceDate is None:
            query += f""",
                julianday(strftime('%Y-%m-%d', FLIGHT_1.departure_datetime) || ' 15:00:00') - julianday(strftime('%Y-%m-%d', '{str(referenceDate)}') || ' 15:00:00') AS days
            """

        if arrivalRegion is None:
            query += f"""
                FROM 
                    (
                        (		
                                    (		
                                                (				
                                                        (
                                                        FLIGHT AS FLIGHT_1 JOIN AIRPORT AS DEPARTURE_AIRPORT ON  FLIGHT_1.departure_airport_code = DEPARTURE_AIRPORT.airport_code
                                                        )
                                                JOIN AIRPORT AS INTERMEDIATE_AIRPORT ON FLIGHT_1.arrival_airport_code = INTERMEDIATE_AIRPORT.airport_code
                                            )
                                    JOIN FLIGHT AS FLIGHT_2 ON FLIGHT_1.arrival_airport_code = FLIGHT_2.departure_airport_code
                                    ) 
                            JOIN AIRPORT AS ARRIVAL_AIRPORT ON FLIGHT_2.arrival_airport_code = ARRIVAL_AIRPORT.airport_code
                        )
                    JOIN AIRLINE AS AIRLINE_1 ON FLIGHT_1.airline_ID = AIRLINE_1.airline_ID
                    )
                JOIN AIRLINE AS AIRLINE_2 ON FLIGHT_2.airline_ID = AIRLINE_2.airline_ID

                WHERE
                    DEPARTURE_AIRPORT.city = '{departureCity}'                                                                          AND
                    FLIGHT_1.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    FLIGHT_2.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    ROUND(((julianday(FLIGHT_2.departure_datetime) - julianday(FLIGHT_1.arrival_datetime)) * 24), 2) BETWEEN 1 AND 6
            """

            if not arrivalCity is None:
                query += f""" AND ARRIVAL_AIRPORT.city = '{arrivalCity}'"""
            else:
                query += f""" AND ARRIVAL_AIRPORT.country = '{arrivalCountry}'"""
        
        else:
            query += f"""
                FROM 
                    (
                                (
                                    (		
                                        (		
                                                    (				
                                                        (
                                                        FLIGHT AS FLIGHT_1 JOIN AIRPORT AS DEPARTURE_AIRPORT ON  FLIGHT_1.departure_airport_code = DEPARTURE_AIRPORT.airport_code
                                                        )
                                                JOIN AIRPORT AS INTERMEDIATE_AIRPORT ON FLIGHT_1.arrival_airport_code = INTERMEDIATE_AIRPORT.airport_code
                                                )
                                            JOIN FLIGHT AS FLIGHT_2 ON FLIGHT_1.arrival_airport_code = FLIGHT_2.departure_airport_code
                                            ) 
                                    JOIN AIRPORT AS ARRIVAL_AIRPORT ON FLIGHT_2.arrival_airport_code = ARRIVAL_AIRPORT.airport_code
                                    )
                            JOIN AIRLINE AS AIRLINE_1 ON FLIGHT_1.airline_ID = AIRLINE_1.airline_ID
                            )
                        JOIN AIRLINE AS AIRLINE_2 ON FLIGHT_2.airline_ID = AIRLINE_2.airline_ID
                        )
                JOIN LOCATION ON (ARRIVAL_AIRPORT.city = LOCATION.city AND ARRIVAL_AIRPORT.country = LOCATION.country)

                WHERE
                    DEPARTURE_AIRPORT.city = '{departureCity}'                                                                          AND
                    FLIGHT_1.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    FLIGHT_2.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    ROUND(((julianday(FLIGHT_2.departure_datetime) - julianday(FLIGHT_1.arrival_datetime)) * 24), 2) BETWEEN 1 AND 6    AND
                    region = '{arrivalRegion}'
            """

        if not departureDate is None:
            query += f""" AND FLIGHT_1.departure_datetime LIKE '{departureDate.strftime('%Y-%m-%d')} __:__:__'"""
        else:
            query += f""" AND FLIGHT_1.departure_datetime LIKE '{travelMonth.strftime('%Y-%m')}-__ __:__:__'"""
        
        if not airline_name is None:
            query += f""" AND AIRLINE_1.airline_ID = AIRLINE_2.airline_ID AND AIRLINE_1.airline_name = '{airline_name}'"""
        if not base_price is None:
            query += f""" AND FLIGHT_1.base_price + FLIGHT_2.base_price < {base_price}"""

        if not travelMonth is None and not referenceDate is None:
            query += f""" AND (julianday(strftime('%Y-%m-%d', FLIGHT_1.departure_datetime) || ' 15:00:00') - julianday(strftime('%Y-%m-%d', '{str(referenceDate)}') || ' 15:00:00')) BETWEEN 1 AND 5
                          AND (julianday(FLIGHT_1.departure_datetime) - julianday('{str(referenceDate)}')) >= 0.5
            
                ORDER BY days DESC, total_duration_HOURS,Total_price,FLIGHT_2.arrival_datetime;
            """
        else:
            query += """ ORDER BY total_duration_HOURS,Total_price,FLIGHT_2.arrival_datetime;"""
        return self.select(query)

    def searchTripsTwoStops(self, departureCity, passengersAdultsAndChildren, arrivalCity=None, arrivalCountry=None, arrivalRegion=None, departureDate=None, travelMonth=None, airline_name=None, base_price=None, referenceDate=None):
        try:
            assert (not arrivalCity is None) or (not arrivalCountry is None) or (not arrivalRegion is None)
            assert (not departureDate is None) or (not travelMonth is None)
        except AssertionError:
            print("A critical internal error occurred. Please refer to the developers, mentioning the error code \"searchTripsTwoStopsAssertionError\". Terminating...")
            sys.exit(-1)
        query = f"""
            SELECT 
                FLIGHT_1.flight_number AS flight_1_number, 
                FLIGHT_1.departure_airport_code,
                DEPARTURE_AIRPORT.city AS departure_city,
                FLIGHT_1.departure_datetime AS flight_1_departure_datetime,
                FLIGHT_1.arrival_airport_code AS intermediate_airport_1_code,
                INTERMEDIATE_AIRPORT_1.city AS intermediate_1_city,
                FLIGHT_1.arrival_datetime AS flight_1_arrival_datetime,
                FLIGHT_1.available_seats AS flight_1_available_seats,
                AIRLINE_1.airline_name AS flight_1_airline_name,
                FLIGHT_1.base_price AS flight_1_base_price,

                FLIGHT_2.flight_number AS flight_2_number,
                FLIGHT_2.departure_airport_code AS intermediate_airport_1_code,
                INTERMEDIATE_AIRPORT_1.city AS intermediate_1_city,
                FLIGHT_2.departure_datetime AS flight_2_departure_datetime, 
                FLIGHT_2.arrival_airport_code AS intermediate_airport_2_code,
                INTERMEDIATE_AIRPORT_2.city AS intermediate_2_city,
                FLIGHT_2.arrival_datetime AS flight_2_arrival_datetime,
                FLIGHT_2.available_seats AS flight_2_available_seats,
                AIRLINE_2.airline_name AS flight_2_airline_name,
                FLIGHT_2.base_price AS flight_2_base_price,
                
                FLIGHT_3.flight_number AS flight_3_number,
                FLIGHT_3.departure_airport_code AS intermediate_airport_2_code,
                INTERMEDIATE_AIRPORT_2.city AS intermediate_2_city,
                FLIGHT_3.departure_datetime AS flight_3_departure_datetime, 
                FLIGHT_3.arrival_airport_code,
                ARRIVAL_AIRPORT.city AS arrival_city,
                FLIGHT_3.arrival_datetime AS flight_3_arrival_datetime,
                FLIGHT_3.available_seats AS flight_3_available_seats,
                AIRLINE_3.airline_name AS flight_3_airline_name,
                FLIGHT_3.base_price AS flight_3_base_price,

                ROUND(((julianday(FLIGHT_3.arrival_datetime) - julianday(FLIGHT_1.departure_datetime)) * 24), 2) AS total_duration_HOURS, 
                FLIGHT_1.base_price + FLIGHT_2.base_price + FLIGHT_3.base_price AS Total_price
            
        """

        if not travelMonth is None and not referenceDate is None:
            query += f""",
                julianday(strftime('%Y-%m-%d', FLIGHT_1.departure_datetime) || ' 15:00:00') - julianday(strftime('%Y-%m-%d', '{str(referenceDate)}') || ' 15:00:00') AS days
            """

        if arrivalRegion is None:
            query += f"""
                FROM          
                            (
                                (
                                        (
                                                (
                                                        (		
                                                                    (		  
                                                                            (		
                                                                                        (
                                                                                        FLIGHT AS FLIGHT_1 JOIN AIRPORT AS DEPARTURE_AIRPORT ON  FLIGHT_1.departure_airport_code = DEPARTURE_AIRPORT.airport_code
                                                                                        )
                                                                                JOIN AIRPORT AS INTERMEDIATE_AIRPORT_1 ON FLIGHT_1.arrival_airport_code = INTERMEDIATE_AIRPORT_1.airport_code
                                                                            )
                                                                    JOIN FLIGHT AS FLIGHT_2 ON FLIGHT_1.arrival_airport_code = FLIGHT_2.departure_airport_code
                                                                    ) 
                                                            JOIN AIRPORT AS INTERMEDIATE_AIRPORT_2 ON FLIGHT_2.arrival_airport_code = INTERMEDIATE_AIRPORT_2.airport_code
                                                        )
                                                    JOIN FLIGHT AS FLIGHT_3 ON FLIGHT_2.arrival_airport_code = FLIGHT_3.departure_airport_code  
                                                )
                                            JOIN AIRPORT AS ARRIVAL_AIRPORT ON FLIGHT_3.arrival_airport_code = ARRIVAL_AIRPORT.airport_code 
                                        )		 
                                    JOIN AIRLINE AS AIRLINE_1 ON FLIGHT_1.airline_ID = AIRLINE_1.airline_ID
                                    )				
                            JOIN AIRLINE AS AIRLINE_2 ON FLIGHT_2.airline_ID = AIRLINE_2.airline_ID
                            )
                    JOIN AIRLINE AS AIRLINE_3 ON FLIGHT_3.airline_ID = AIRLINE_3.airline_ID
                    
                WHERE
                    DEPARTURE_AIRPORT.city = '{departureCity}'                                                                          AND
                    ROUND(((julianday(FLIGHT_2.departure_datetime) - julianday(FLIGHT_1.arrival_datetime)) * 24), 2) BETWEEN 1 AND 6    AND
                    ROUND(((julianday(FLIGHT_3.departure_datetime) - julianday(FLIGHT_2.arrival_datetime)) * 24), 2) BETWEEN 1 AND 6    AND
                    INTERMEDIATE_AIRPORT_1.city != ARRIVAL_AIRPORT.city                                                                 AND
                    INTERMEDIATE_AIRPORT_2.city != DEPARTURE_AIRPORT.city                                                               AND
                    FLIGHT_1.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    FLIGHT_2.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    FLIGHT_3.available_seats >= {passengersAdultsAndChildren}
            """

            if not arrivalCity is None:
                query += f""" AND ARRIVAL_AIRPORT.city = '{arrivalCity}'"""
            else:
                query += f""" AND ARRIVAL_AIRPORT.country = '{arrivalCountry}'"""
        
        else:
            query += f"""
                FROM          
                        (
                            (
                                (
                                        (
                                                (
                                                        (		
                                                                    (		  
                                                                            (		
                                                                                        (
                                                                                        FLIGHT AS FLIGHT_1 JOIN AIRPORT AS DEPARTURE_AIRPORT ON  FLIGHT_1.departure_airport_code = DEPARTURE_AIRPORT.airport_code
                                                                                        )
                                                                                JOIN AIRPORT AS INTERMEDIATE_AIRPORT_1 ON FLIGHT_1.arrival_airport_code = INTERMEDIATE_AIRPORT_1.airport_code
                                                                            )
                                                                    JOIN FLIGHT AS FLIGHT_2 ON FLIGHT_1.arrival_airport_code = FLIGHT_2.departure_airport_code
                                                                    ) 
                                                            JOIN AIRPORT AS INTERMEDIATE_AIRPORT_2 ON FLIGHT_2.arrival_airport_code = INTERMEDIATE_AIRPORT_2.airport_code
                                                        )
                                                    JOIN FLIGHT AS FLIGHT_3 ON FLIGHT_2.arrival_airport_code = FLIGHT_3.departure_airport_code  
                                                )
                                            JOIN AIRPORT AS ARRIVAL_AIRPORT ON FLIGHT_3.arrival_airport_code = ARRIVAL_AIRPORT.airport_code 
                                        )		 
                                    JOIN AIRLINE AS AIRLINE_1 ON FLIGHT_1.airline_ID = AIRLINE_1.airline_ID
                                    )				
                            JOIN AIRLINE AS AIRLINE_2 ON FLIGHT_2.airline_ID = AIRLINE_2.airline_ID
                            )
                        JOIN AIRLINE AS AIRLINE_3 ON FLIGHT_3.airline_ID = AIRLINE_3.airline_ID
                    )
                    JOIN LOCATION ON (ARRIVAL_AIRPORT.city = LOCATION.city AND ARRIVAL_AIRPORT.country = LOCATION.country)
                    
                WHERE
                    DEPARTURE_AIRPORT.city = '{departureCity}'                                                                          AND
                    ROUND(((julianday(FLIGHT_2.departure_datetime) - julianday(FLIGHT_1.arrival_datetime)) * 24), 2) BETWEEN 1 AND 6    AND
                    ROUND(((julianday(FLIGHT_3.departure_datetime) - julianday(FLIGHT_2.arrival_datetime)) * 24), 2) BETWEEN 1 AND 6    AND
                    INTERMEDIATE_AIRPORT_1.city != ARRIVAL_AIRPORT.city                                                                 AND
                    INTERMEDIATE_AIRPORT_2.city != DEPARTURE_AIRPORT.city                                                               AND
                    FLIGHT_1.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    FLIGHT_2.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    FLIGHT_3.available_seats >= {passengersAdultsAndChildren}                                                           AND
                    region = '{arrivalRegion}'
            """

        if not departureDate is None:
            query += f""" AND FLIGHT_1.departure_datetime LIKE '{departureDate.strftime('%Y-%m-%d')} __:__:__'"""
        else:
            query += f""" AND FLIGHT_1.departure_datetime LIKE '{travelMonth.strftime('%Y-%m')}-__ __:__:__'"""

        if not airline_name is None:
            query += f""" AND AIRLINE_1.airline_ID = AIRLINE_2.airline_ID AND AIRLINE_2.airline_ID = AIRLINE_3.airline_ID AND AIRLINE_1.airline_name = '{airline_name}'"""
        if not base_price is None:
            query += f""" AND FLIGHT_1.base_price + FLIGHT_2.base_price + FLIGHT_3.base_price < {base_price}"""
        
        if not travelMonth is None and not referenceDate is None:
            query += f""" AND (julianday(strftime('%Y-%m-%d', FLIGHT_1.departure_datetime) || ' 15:00:00') - julianday(strftime('%Y-%m-%d', '{str(referenceDate)}') || ' 15:00:00')) BETWEEN 1 AND 5
                          AND (julianday(FLIGHT_1.departure_datetime) - julianday('{str(referenceDate)}')) >= 0.5
                ORDER BY days DESC, total_duration_HOURS,Total_price,FLIGHT_3.arrival_datetime;
            """
        else:
            query += """ ORDER BY total_duration_HOURS,Total_price,FLIGHT_3.arrival_datetime;"""
        return self.select(query)

    def getAvailableFares(self, airline_ID):
        return self.select(f"""
            SELECT *
            FROM FARE
            WHERE airline_ID = '{airline_ID}'
        """)

    def getAllAgePolicies(self):
        return self.select("""
            SELECT *
            FROM AGE_POLICY NATURAL JOIN AIRLINE;
        """)
    
    def getAvailableAgePolicies(self, airline_ID):
        return self.select(f"""
            SELECT *
            FROM AGE_POLICY
            WHERE airline_ID = '{airline_ID}'
        """)

    def getAvailableSeats(self, flight_number, departure_date):
        return self.select(f"""
            SELECT seat_number,seat_class

            FROM SEAT_MAP NATURAL JOIN ( 
                                SELECT aircraft_type
                                FROM FLIGHT 
                                WHERE 
                                flight_number = '{flight_number}' 				  AND 
                                departure_datetime LIKE '{departure_date} __:__:__'
                            )	
                                        
            WHERE seat_number NOT IN   (
                                SELECT seat_number
                                FROM TAKEN_SEAT
                                WHERE 
                                flight_number = '{flight_number}' 				  AND 
                                departure_datetime LIKE '{departure_date} __:__:__'
                            )

            ORDER BY seat_number;
        """)

    def getLuggageTypes(self, airline_ID):
        return self.select(f"""
            SELECT *
            FROM LUGGAGE_TYPE
            WHERE airline_ID = '{airline_ID}'
        """)
    
    def savePassenger(self, passenger):
        if len(self.select(f"SELECT * FROM PASSENGER WHERE passenger_ID = '{passenger.passenger_ID}';")) > 0:
            query = f"""
                UPDATE PASSENGER
                SET 
                    first_name = "{passenger.first_name}",
                    last_name = "{passenger.last_name}",
                    age = "{passenger.age}",
                    phone_number = {f'"{passenger.phone_number}"' if passenger.phone_number is not None else "NULL"},
                    email = {f'"{passenger.email}"' if passenger.email is not None else "NULL"}
                WHERE passenger_ID = '{passenger.passenger_ID}'
            """
        else:
            query = f"""
                INSERT INTO "PASSENGER" VALUES
                ("{passenger.passenger_ID}", "{passenger.first_name}", "{passenger.last_name}", "{passenger.age}", {f'"{passenger.phone_number}"' if passenger.phone_number is not None else "NULL"}, {f'"{passenger.email}"' if passenger.email is not None else "NULL"});
            """

        self.conn.execute(query)
        return True

    def saveBooking(self, booking):
        query = f"""
            INSERT INTO "BOOKING" VALUES
            ("{booking.booking_code}", "{booking.booking_date.strftime('%Y-%m-%d %H:%M:%S')}", "{booking.total_price}", "{booking.main_passenger_ID}");
        """
        self.conn.execute(query)
        return True
    
    def saveTakenSeat(self, takenSeat):
        self.conn.execute(f"""
            INSERT INTO "TAKEN_SEAT" VALUES
            ("{takenSeat.seat_number}", "{takenSeat.flight_number}", "{str(takenSeat.departure_datetime)}");
        """)
        self.conn.execute(f"""
            UPDATE FLIGHT
            SET available_seats = available_seats - 1
            WHERE flight_number = "{takenSeat.flight_number}" AND "{str(takenSeat.departure_datetime)}";
        """)
        return True

    def saveTicket(self, ticket):
        query = f"""
            INSERT INTO "TICKET" VALUES
            ("{ticket.ticket_ID}", "{ticket.price}", "{ticket.seat_number}", "{ticket.flight_number}", "{str(ticket.departure_datetime)}", "{ticket.passenger_ID}", "{ticket.booking_code}", "{ticket.fare_name}", "{ticket.airline_ID}");
        """
        self.conn.execute(query)
        return True
    
    def saveLuggage(self, luggage):
        self.conn.execute(f"""
            INSERT INTO "LUGGAGE" VALUES
            ("{luggage.luggage_ID}", "{luggage.ticket_ID}", "{luggage.airline_ID}", "{luggage.weight}");
        """)
        return True
    
    def commitChanges(self):
        self.conn.commit()
        return True
    
    def rollbackChanges(self):
        self.conn.rollback()
        return True

    def calculateTicketPrice(self, maxAge, luggageList, flight_number, departure_datetime, fare_name):
        query = """
            SELECT
                flight_number,
                departure_datetime,
                airline_name,
        """

        if maxAge == None:
            query += """
                    ROUND(fare_price_coefficient * base_price
            """
        else:
            query += """
                    ROUND(fare_price_coefficient * age_price_coefficient * base_price
            """

        for i in range(len(luggageList)):
            query += f""" + LUGGAGE_{i}.cost """

        query += ", 2) AS price"
        
        query += """
            FROM 
        """

        if maxAge is None:
            for _ in range(len(luggageList)+1):
                query += """ ( """ 
        else:
            for _ in range(len(luggageList)+2):
                query += """ ( """
            
        query += """
                FLIGHT NATURAL JOIN FARE) NATURAL JOIN AIRLINE
        """

        if maxAge is not None:
            query += """ ) NATURAL JOIN AGE_POLICY """

        for i in range(len(luggageList)):
            query += f"""
                ) JOIN LUGGAGE_TYPE AS LUGGAGE_{i} ON AIRLINE.airline_ID = LUGGAGE_{i}.airline_ID
            """

        query += f"""
            WHERE
                flight_number = '{flight_number}'       AND
                departure_datetime = '{str(departure_datetime)}'   AND
                fare_name = '{fare_name}'
        """

        if maxAge is not None:
            query += f""" AND max_age = {maxAge} """
        
        for i in range(len(luggageList)):
            query += f""" AND LUGGAGE_{i}.weight = {luggageList[i]} """

        query += ';'

        data = self.select(query)
        return round(data[0][-1], 2)