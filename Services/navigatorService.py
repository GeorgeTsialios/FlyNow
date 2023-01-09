from datetime import datetime
from HelperClasses.trip import Trip
from Model.flight import Flight
from Model.seatmap import Seatmap
from Model.takenseat import TakenSeat
from Model.fare import Fare
from Model.agepolicy import AgePolicy
from Model.luggagetype import LuggageType
from Model.luggage import Luggage
from Model.passenger import Passenger
from Model.booking import Booking
from Model.ticket import Ticket
from HelperClasses.ticketGenerator import TicketGenerator
import sys
import re

class NavigatorService:
    def __init__(self, app):
        self.app = app
        self.ticketGenerator = TicketGenerator()
        self.mainMenu()

    def mainMenu(self):
        while True:
            options = [
                "\nMain menu options:",
                "- Press 1 to start planning a new trip.",
                "- Press ? for help.",
                "- Press * to exit."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                print("Exiting...")
                break
            elif userInput == '?':
                self.helpMenu()
            else:
                try:
                    numericUserInput = int(userInput)

                    if numericUserInput == 1:
                        userChoices = self.newTripMenu()
                        if userChoices is None:
                            continue

                        print("\nSearching for flights that suit your preferences...")
                        suitableTrips = self.searchForTrips(userChoices)
                        selectedTrip = self.displaySuitableTrips(suitableTrips)
                        if selectedTrip is None:
                            continue
                        
                        selectedReturnTrip = None
                        if userChoices['roundTrip']:
                            print("\nSearching for return flights that suit your preferences...")
                            suitableTrips = self.searchForTrips(userChoices, departTrip=selectedTrip)
                            selectedReturnTrip = self.displaySuitableTrips(suitableTrips)
                            if selectedReturnTrip is None:
                                continue
                        
                        booking = self.makeBooking(selectedTrip, userChoices, returnTrip=selectedReturnTrip)
                        if booking is None:
                            continue
                        elif booking:
                            print("\nReturning to main menu...")
                    else:
                        raise ValueError

                except ValueError:
                    print("Invalid input. Please try again.")

    def newTripMenu(self):
        while True:
            options = [
                "\nNew trip menu options:",
                "- Press 1 to begin a round trip.",
                "- Press 2 to begin an one-way trip.",
                "- Press * to return to main menu."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                return None
            else:
                try:
                    numericUserInput = int(userInput)

                    if numericUserInput == 1:
                        flightUserChoices = self.flightSelectionMenu(roundTrip=True)
                    elif numericUserInput == 2:
                        flightUserChoices = self.flightSelectionMenu(roundTrip=False)
                    else:
                        raise ValueError

                    if flightUserChoices is None:
                        print('Your trip is discarded. Returning to main menu...')
                        return None
                    else:
                        if numericUserInput == 1:
                            flightUserChoices['roundTrip'] = True
                        else:
                            flightUserChoices['roundTrip'] = False
                        
                        return flightUserChoices
                    
                except ValueError:
                    print("Invalid input. Please try again.")

    def flightSelectionMenu(self, roundTrip):
        userChoicesDict = {}

        userValues = self.originSelectionMenu()
        if userValues == (False, False):
            return None
        else:
            userChoicesDict[userValues[0]] = userValues[1]

        userValues = self.destinationSelectionMenu()
        if userValues == (False, False):
            return None
        else:
            userChoicesDict[userValues[0]] = userValues[1]

        userValues = self.datesSelectionMenu(roundTrip)
        if userValues == (False, False):
            return None
        else:
            for userValue in userValues:
                userChoicesDict[userValue[0]] = userValue[1]

        userValues = self.passengersSelectionMenu()
        if userValues == (False, False):
            return None
        else:
            for userValue in userValues:
                userChoicesDict[userValue[0]] = userValue[1]

        userValues = self.airlineSelectionMenu()
        if userValues == False:
            return None
        elif not userValues is None:
            userChoicesDict['airlineName'] = userValues

        userValues = self.priceSelectionMenu()
        if userValues == False:
            return None
        elif not userValues is None:
            userChoicesDict['basePrice'] = userValues

        userValues = self.stopsSelectionMenu()
        if type(userValues) != int and userValues == False:
            return None
        elif not userValues is None:
            userChoicesDict['numberOfStops'] = userValues

        return userChoicesDict
       
    def originSelectionMenu(self):
        while True:
            options = [
                "\nWhere do you want to travel from?"
            ]

            for option in options:
                print(option)
            origUserInput = input("Enter a city: ")

            try:
                if origUserInput == '*':
                    return False, False
                if origUserInput not in self.app.cities:
                    raise IndexError(f"{origUserInput} is not a valid city, or is not currently supported. Please try again.")
                else:
                    print(f"{origUserInput} selected.")
                    return "originCity", origUserInput
            except IndexError as e:
                print(e.args[0])

    def destinationSelectionMenu(self):
        while True:
            options = [
                "\nWhere do you want to travel to?",
                "- Press 1 to select a city.",
                "- Press 2 to select a country.",
                "- Press 3 to select a region.",
                "- Press * to return to main menu."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                return False, False
            else:
                try:
                    numericUserInput = int(userInput)

                    if numericUserInput == 1:
                        destUserInput = input("Enter a city: ")
                        if destUserInput not in self.app.cities:
                            raise IndexError(f"{destUserInput} is not a valid city, or is not currently supported. Please try again.")
                        else:
                            print(f"{destUserInput} selected.")
                            return 'destinationCity', destUserInput
                    elif numericUserInput == 2:
                        destUserInput = input("Enter a country: ")
                        if destUserInput not in self.app.countries:
                            raise IndexError(f"{destUserInput} is not a valid country, or is not currently supported. Please try again.")
                        else:
                            print(f"{destUserInput} selected.")
                            return 'destinationCountry', destUserInput
                    elif numericUserInput == 3:
                        destUserInput = input("Enter a region: ")
                        if destUserInput not in self.app.regions:
                            raise IndexError(f"{destUserInput} is not a valid region, or is not currently supported. Please try again.")
                        else:
                            print(f"{destUserInput} selected.")
                            return 'destinationRegion', destUserInput
                    else:
                        raise ValueError

                except ValueError:
                    print("Invalid input. Please try again.")
                except IndexError as e:
                    print(e.args[0])
    
    def datesSelectionMenu(self, roundTrip):
        while True:
            options = [
                "\nWhen do you want to travel?",
                "- Press 1 to select specific dates." if roundTrip else "- Press 1 to select a specific date.",
                "- Press 2 to select a whole month.",
                "- Press * to return to main menu."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                return False, False
            else:
                try:
                    numericUserInput = int(userInput)
                    output = []

                    if numericUserInput == 1:
                        departureDateUserInput = input("When do you want to depart?\nEnter a date in the format YYYY/MM/DD: ")
                        try:
                            departureDateUserInputParsed = datetime.strptime(departureDateUserInput, '%Y/%m/%d').date()
                            if departureDateUserInputParsed < datetime.now().date():
                                raise IndexError("The departure date cannot be in the past. Please try again.")
                        except ValueError:
                            raise IndexError("Invalid date format entered. Please try again.")
                        output.append(('departDate', departureDateUserInputParsed))

                        if roundTrip:
                            returnDateUserInput = input("When do you want to return?\nEnter a date in the format YYYY/MM/DD: ")
                            try:
                                returnDateUserInputParsed = datetime.strptime(returnDateUserInput, '%Y/%m/%d').date()
                                if returnDateUserInputParsed < departureDateUserInputParsed:
                                    raise IndexError("The return date cannot be past the departure date. Please try again.")
                            except ValueError:
                                raise IndexError("Invalid date format entered. Please try again.")
                            output.append(('returnDate', returnDateUserInputParsed))
                        return output
                    elif numericUserInput == 2:
                        monthUserInput = input("Enter a date in the format YYYY/MM: ")
                        try:
                            monthUserInputParsed = datetime.strptime(monthUserInput, '%Y/%m').date()
                            if monthUserInputParsed < datetime.now().date().replace(day=1):
                                raise IndexError("The travel month cannot be in the past. Please try again.")
                        except ValueError:
                            raise IndexError("Invalid date format entered. Please try again.")
                        output.append(('travelMonth', monthUserInputParsed))
                        return output
                    else:
                        raise ValueError
                except ValueError:
                    print("Invalid input. Please try again.")
                except IndexError as e:
                    print(e.args[0])

    def passengersSelectionMenu(self):
        while True:
            try:
                output = []

                adultsUserInput = input("\nHow many adults (12 y.o. or older) are going to travel? ")
                numericAdultsUserInput = int(adultsUserInput)
                if numericAdultsUserInput < 0:
                    raise IndexError("Invalid input. Please try again.")
                if numericAdultsUserInput < 1:
                    raise IndexError("There must be at least one adult in the booking. Please try again.")
                if numericAdultsUserInput > 9:
                    raise IndexError("The booking cannot contain more than 9 passengers. Please try again.")
                output.append(("passengersAdults", numericAdultsUserInput))

                childrenUserInput = input("How many children (2-11 y.o.) are going to travel? ")
                numericChildrenUserInput = int(childrenUserInput)
                if numericChildrenUserInput < 0:
                    raise IndexError("Invalid input. Please try again.")
                if numericAdultsUserInput + numericChildrenUserInput > 9:
                    raise IndexError("The booking cannot contain more than 9 passengers. Please try again.")
                output.append(("passengersChildren", numericChildrenUserInput))

                infantsUserInput = input("How many infants (<2 y.o.) are going to travel? ")
                numericInfantsUserInput = int(infantsUserInput)
                if numericInfantsUserInput < 0:
                    raise IndexError("Invalid input. Please try again.")
                if numericInfantsUserInput > numericAdultsUserInput:
                    raise IndexError("There can be no more infants than adults in the same booking. Please try again.")
                if numericAdultsUserInput + numericChildrenUserInput + numericInfantsUserInput > 9:
                    raise IndexError("The booking cannot contain more than 9 passengers. Please try again.")
                output.append(("passengersInfants", numericInfantsUserInput))
                
                return output
            
            except ValueError:
                print("Invalid input. Please try again.")
            except IndexError as e:
                print(e.args[0])

    def airlineSelectionMenu(self):
        while True:
            options = [
                "\nDo you want to travel with a specific airline?",
                "Enter the airline name, or leave the field blank to override this filter."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                return False
            elif userInput == '':
                return None
            else:
                try:
                    if userInput in [airline.airline_name for airline in self.app.airlines]:
                        return userInput
                    else:
                        raise IndexError("Invalid airline name entered. Please try again.")
                except IndexError as e:
                    print(e.args[0])
    
    def priceSelectionMenu(self):
        while True:
            options = [
                "\nDo you want to set a maximum base price for your flight?",
                "Enter the desired maximum price, or leave the field blank to override this filter."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")
            userInput = userInput.replace(',','.')

            if userInput == '*':
                return False
            elif userInput == '':
                return None
            else:
                try:
                    numericUserInput = float(userInput)
                    if numericUserInput <= 0:
                        raise ValueError
                    return numericUserInput
                except ValueError:
                    print("Invalid price entered. Please try again.")

    def stopsSelectionMenu(self):
        while True:
            options = [
                "\nDo you want to set a maximum number of stops for your flight?",
                "Enter the desired maximum number of stops, or leave the field blank to override this filter."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                return False
            elif userInput == '':
                return None
            else:
                try:
                    numericUserInput = int(userInput)
                    if numericUserInput < 0 or numericUserInput > 2:
                        return numericUserInput
                    return numericUserInput
                except ValueError:
                    print("Invalid number of stops entered. The maximum permitted number of stops is 2. Please try again.")

    def searchForTrips(self, userChoices, departTrip=None):
        suitableTrips = []
        agePolicies = []

        agePolicyData = self.app.databaseService.getAllAgePolicies()
        for datum in agePolicyData:
            agePolicies.append(AgePolicy(
                datum[3],
                int(datum[1]),
                float(datum[2])
            ))

        print('Searching for non-stop flights...')

        if departTrip is None:
            zeroStopsData = self.app.databaseService.searchTripsZeroStops(
                departureCity = userChoices['originCity'],
                passengersAdultsAndChildren = userChoices['passengersAdults'] + userChoices['passengersChildren'],
                arrivalCity = userChoices['destinationCity'] if 'destinationCity' in userChoices else None,
                arrivalCountry = userChoices['destinationCountry'] if 'destinationCountry' in userChoices else None,
                arrivalRegion = userChoices['destinationRegion'] if 'destinationRegion' in userChoices else None,
                departureDate = userChoices['departDate'] if 'departDate' in userChoices else None,
                travelMonth = userChoices['travelMonth'] if 'travelMonth' in userChoices else None,
                airline_name = userChoices['airlineName'] if 'airlineName' in userChoices else None,
                base_price = userChoices['basePrice'] if 'basePrice' in userChoices else None
            )
        else:
            zeroStopsData = self.app.databaseService.searchTripsZeroStops(
                departureCity = next(item for item in self.app.airports if item.airport_code == departTrip.flights[-1].arrival_airport_code).city,
                passengersAdultsAndChildren = userChoices['passengersAdults'] + userChoices['passengersChildren'],
                arrivalCity = userChoices['originCity'],
                departureDate = userChoices['returnDate'] if 'returnDate' in userChoices else None,
                travelMonth = userChoices['travelMonth'] if 'travelMonth' in userChoices else None,
                referenceDate = departTrip.flights[-1].arrival_datetime if 'travelMonth' in userChoices else None,
                airline_name = userChoices['airlineName'] if 'airlineName' in userChoices else None,
                base_price = userChoices['basePrice']-departTrip.totalPrice if 'basePrice' in userChoices else None
            )
        overridden = 0

        for datum in zeroStopsData:
            try:
                newTrip = Trip()
                newTrip.addFlight(Flight(
                    datum[0],
                    datetime.strptime(datum[3], '%Y-%m-%d %H:%M:%S'),
                    None,
                    datum[1],
                    datetime.strptime(datum[6], '%Y-%m-%d %H:%M:%S'),
                    datum[4],
                    datum[7],
                    datum[9],
                    round(datum[10], 2),
                    datum[8],
                    departure_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[1]),
                    arrival_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[4])
                ))
            except StopIteration:
                print("A critical internal error occurred. Please refer to the developers, mentioning the error code \"airportProgramDatabaseMismatch\". Terminating...")
                sys.exit(-1)
            newTrip.setTotalDuration(datum[9])

            totalPrice = 0
            if userChoices['passengersAdults'] > 0:
                totalPrice += userChoices['passengersAdults'] * self.app.databaseService.calculateTicketPrice(None, [], datum[0], datum[3], 'Economy Light')
            if userChoices['passengersChildren'] > 0:
                totalPrice += userChoices['passengersChildren'] * self.app.databaseService.calculateTicketPrice(12, [], datum[0], datum[3], 'Economy Light')
            if userChoices['passengersInfants'] > 0:
                totalPrice += userChoices['passengersInfants'] * self.app.databaseService.calculateTicketPrice(2, [], datum[0], datum[3], 'Economy Light')
            newTrip.flights[0].setPriceForPassengers(totalPrice)

            if 'basePrice' in userChoices and ((departTrip is None and totalPrice > userChoices['basePrice']) or (departTrip is not None and totalPrice > userChoices['basePrice'] - departTrip.totalPrice)):
                del newTrip
                overridden += 1
                continue

            newTrip.setTotalPrice(round(totalPrice, 2))
            suitableTrips.append(newTrip)

        print(f'Found {len(zeroStopsData)-overridden} non-stop flights.')

        if 'numberOfStops' not in userChoices or ('numberOfStops' in userChoices and userChoices['numberOfStops'] > 0):

            print('Searching for one-stop flights...')
            
            if departTrip is None:
                oneStopData = self.app.databaseService.searchTripsOneStop(
                    departureCity = userChoices['originCity'],
                    passengersAdultsAndChildren = userChoices['passengersAdults'] + userChoices['passengersChildren'],
                    arrivalCity = userChoices['destinationCity'] if 'destinationCity' in userChoices else None,
                    arrivalCountry = userChoices['destinationCountry'] if 'destinationCountry' in userChoices else None,
                    arrivalRegion = userChoices['destinationRegion'] if 'destinationRegion' in userChoices else None,
                    departureDate = userChoices['departDate'] if 'departDate' in userChoices else None,
                    travelMonth = userChoices['travelMonth'] if 'travelMonth' in userChoices else None,
                    airline_name = userChoices['airlineName'] if 'airlineName' in userChoices else None,
                    base_price = userChoices['basePrice'] if 'basePrice' in userChoices else None
                )
            else:
                oneStopData = self.app.databaseService.searchTripsOneStop(
                    departureCity = next(item for item in self.app.airports if item.airport_code == departTrip.flights[-1].arrival_airport_code).city,
                    passengersAdultsAndChildren = userChoices['passengersAdults'] + userChoices['passengersChildren'],
                    arrivalCity = userChoices['originCity'],
                    departureDate = userChoices['returnDate'] if 'returnDate' in userChoices else None,
                    travelMonth = userChoices['travelMonth'] if 'travelMonth' in userChoices else None,
                    referenceDate = departTrip.flights[-1].arrival_datetime if 'travelMonth' in userChoices else None,
                    airline_name = userChoices['airlineName'] if 'airlineName' in userChoices else None,
                    base_price = userChoices['basePrice']-departTrip.totalPrice if 'basePrice' in userChoices else None
                )
            overridden = 0

            for datum in oneStopData:
                try:
                    newTrip = Trip()
                    newTrip.addFlight(Flight(
                        datum[0],
                        datetime.strptime(datum[3], '%Y-%m-%d %H:%M:%S'),
                        None,
                        datum[1],
                        datetime.strptime(datum[6], '%Y-%m-%d %H:%M:%S'),
                        datum[4],
                        datum[7],
                        None,
                        datum[9],
                        datum[8],
                        departure_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[1]),
                        arrival_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[4])
                    ))
                    newTrip.addFlight(Flight(
                        datum[10],
                        datetime.strptime(datum[13], '%Y-%m-%d %H:%M:%S'),
                        None,
                        datum[11],
                        datetime.strptime(datum[16], '%Y-%m-%d %H:%M:%S'),
                        datum[14],
                        datum[17],
                        None,
                        datum[19],
                        datum[18],
                        departure_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[11]),
                        arrival_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[14])
                    ))
                except StopIteration:
                    print("A critical internal error occurred. Please refer to the developers, mentioning the error code \"airportProgramDatabaseMismatch\". Terminating...")
                    sys.exit(-1)
                newTrip.setTotalDuration(round(datum[20] * 60))

                totalPrice0 = 0
                if userChoices['passengersAdults'] > 0:
                    totalPrice0 += userChoices['passengersAdults'] * self.app.databaseService.calculateTicketPrice(None, [], datum[0], datum[3], 'Economy Light')
                if userChoices['passengersChildren'] > 0:
                    totalPrice0 += userChoices['passengersChildren'] * self.app.databaseService.calculateTicketPrice(12, [], datum[0], datum[3], 'Economy Light')
                if userChoices['passengersInfants'] > 0:
                    totalPrice0 += userChoices['passengersInfants'] * self.app.databaseService.calculateTicketPrice(2, [], datum[0], datum[3], 'Economy Light')
                newTrip.flights[0].setPriceForPassengers(totalPrice0)

                totalPrice1 = 0
                if userChoices['passengersAdults'] > 0:
                    totalPrice1 += userChoices['passengersAdults'] * self.app.databaseService.calculateTicketPrice(None, [], datum[10], datum[13], 'Economy Light')
                if userChoices['passengersChildren'] > 0:
                    totalPrice1 += userChoices['passengersChildren'] * self.app.databaseService.calculateTicketPrice(12, [], datum[10], datum[13], 'Economy Light')
                if userChoices['passengersInfants'] > 0:
                    totalPrice1 += userChoices['passengersInfants'] * self.app.databaseService.calculateTicketPrice(2, [], datum[10], datum[13], 'Economy Light')
                newTrip.flights[1].setPriceForPassengers(totalPrice1)
                
                totalPrice = totalPrice0 + totalPrice1

                if 'basePrice' in userChoices and ((departTrip is None and totalPrice > userChoices['basePrice']) or (departTrip is not None and totalPrice > userChoices['basePrice'] - departTrip.totalPrice)):
                    del newTrip
                    overridden += 1
                    continue

                newTrip.setTotalPrice(round(totalPrice, 2))
                suitableTrips.append(newTrip)
            
            print(f'Found {len(oneStopData)-overridden} one-stop flights.')

        if 'numberOfStops' not in userChoices or ('numberOfStops' in userChoices and userChoices['numberOfStops'] > 1):

            print('Searching for two-stops flights...')

            if departTrip is None:
                twoStopsData = self.app.databaseService.searchTripsTwoStops(
                    departureCity = userChoices['originCity'],
                    passengersAdultsAndChildren = userChoices['passengersAdults'] + userChoices['passengersChildren'],
                    arrivalCity = userChoices['destinationCity'] if 'destinationCity' in userChoices else None,
                    arrivalCountry = userChoices['destinationCountry'] if 'destinationCountry' in userChoices else None,
                    arrivalRegion = userChoices['destinationRegion'] if 'destinationRegion' in userChoices else None,
                    departureDate = userChoices['departDate'] if 'departDate' in userChoices else None,
                    travelMonth = userChoices['travelMonth'] if 'travelMonth' in userChoices else None,
                    airline_name = userChoices['airlineName'] if 'airlineName' in userChoices else None,
                    base_price = userChoices['basePrice'] if 'basePrice' in userChoices else None
                )
            else:
                twoStopsData = self.app.databaseService.searchTripsTwoStops(
                    departureCity = next(item for item in self.app.airports if item.airport_code == departTrip.flights[-1].arrival_airport_code).city,
                    passengersAdultsAndChildren = userChoices['passengersAdults'] + userChoices['passengersChildren'],
                    arrivalCity = userChoices['originCity'],
                    departureDate = userChoices['returnDate'] if 'returnDate' in userChoices else None,
                    travelMonth = userChoices['travelMonth'] if 'travelMonth' in userChoices else None,
                    referenceDate = departTrip.flights[-1].arrival_datetime if 'travelMonth' in userChoices else None,
                    airline_name = userChoices['airlineName'] if 'airlineName' in userChoices else None,
                    base_price = userChoices['basePrice']-departTrip.totalPrice if 'basePrice' in userChoices else None
                )
            overridden = 0

            for datum in twoStopsData:
                try:
                    newTrip = Trip()
                    newTrip.addFlight(Flight(
                        datum[0],
                        datetime.strptime(datum[3], '%Y-%m-%d %H:%M:%S'),
                        None,
                        datum[1],
                        datetime.strptime(datum[6], '%Y-%m-%d %H:%M:%S'),
                        datum[4],
                        datum[7],
                        None,
                        datum[9],
                        datum[8],
                        departure_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[1]),
                        arrival_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[4])
                    ))
                    newTrip.addFlight(Flight(
                        datum[10],
                        datetime.strptime(datum[13], '%Y-%m-%d %H:%M:%S'),
                        None,
                        datum[11],
                        datetime.strptime(datum[16], '%Y-%m-%d %H:%M:%S'),
                        datum[14],
                        datum[17],
                        None,
                        datum[19],
                        datum[18],
                        departure_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[11]),
                        arrival_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[14])
                    ))
                    newTrip.addFlight(Flight(
                        datum[20],
                        datetime.strptime(datum[23], '%Y-%m-%d %H:%M:%S'),
                        None,
                        datum[21],
                        datetime.strptime(datum[26], '%Y-%m-%d %H:%M:%S'),
                        datum[24],
                        datum[27],
                        None,
                        datum[29],
                        datum[28],
                        departure_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[21]),
                        arrival_airport_object = next(airport for airport in self.app.airports if airport.airport_code == datum[24])
                    ))
                except StopIteration:
                    print("A critical internal error occurred. Please refer to the developers, mentioning the error code \"airportProgramDatabaseMismatch\". Terminating...")
                    sys.exit(-1)
                newTrip.setTotalDuration(round(datum[30] * 60))

                totalPrice0 = 0
                if userChoices['passengersAdults'] > 0:
                    totalPrice0 += userChoices['passengersAdults'] * self.app.databaseService.calculateTicketPrice(None, [], datum[0], datum[3], 'Economy Light')
                if userChoices['passengersChildren'] > 0:
                    totalPrice0 += userChoices['passengersChildren'] * self.app.databaseService.calculateTicketPrice(12, [], datum[0], datum[3], 'Economy Light')
                if userChoices['passengersInfants'] > 0:
                    totalPrice0 += userChoices['passengersInfants'] * self.app.databaseService.calculateTicketPrice(2, [], datum[0], datum[3], 'Economy Light')
                newTrip.flights[0].setPriceForPassengers(totalPrice0)

                totalPrice1 = 0
                if userChoices['passengersAdults'] > 0:
                    totalPrice1 += userChoices['passengersAdults'] * self.app.databaseService.calculateTicketPrice(None, [], datum[10], datum[13], 'Economy Light')
                if userChoices['passengersChildren'] > 0:
                    totalPrice1 += userChoices['passengersChildren'] * self.app.databaseService.calculateTicketPrice(12, [], datum[10], datum[13], 'Economy Light')
                if userChoices['passengersInfants'] > 0:
                    totalPrice1 += userChoices['passengersInfants'] * self.app.databaseService.calculateTicketPrice(2, [], datum[10], datum[13], 'Economy Light')
                newTrip.flights[1].setPriceForPassengers(totalPrice1)

                totalPrice2 = 0
                if userChoices['passengersAdults'] > 0:
                    totalPrice2 += userChoices['passengersAdults'] * self.app.databaseService.calculateTicketPrice(None, [], datum[20], datum[23], 'Economy Light')
                if userChoices['passengersChildren'] > 0:
                    totalPrice2 += userChoices['passengersChildren'] * self.app.databaseService.calculateTicketPrice(12, [], datum[20], datum[23], 'Economy Light')
                if userChoices['passengersInfants'] > 0:
                    totalPrice2 += userChoices['passengersInfants'] * self.app.databaseService.calculateTicketPrice(2, [], datum[20], datum[23], 'Economy Light')
                newTrip.flights[1].setPriceForPassengers(totalPrice2)
                
                totalPrice = totalPrice0 + totalPrice1 + totalPrice2

                if 'basePrice' in userChoices and ((departTrip is None and totalPrice > userChoices['basePrice']) or (departTrip is not None and totalPrice > userChoices['basePrice'] - departTrip.totalPrice)):
                    del newTrip
                    overridden += 1
                    continue

                newTrip.setTotalPrice(round(totalPrice, 2))
                suitableTrips.append(newTrip)

            print(f'Found {len(twoStopsData)-overridden} two-stops flights.')

        return suitableTrips
    
    def displaySuitableTrips(self, suitableTrips):
        if len(suitableTrips) == 0:
            print("No trips found. Please change your criteria and try again.")
            return None

        tripMinIndex = 1
        tripMaxIndex = -1
        while tripMaxIndex != len(suitableTrips):
            tripMaxIndex = min(tripMinIndex+10, len(suitableTrips))+1
            for index in range(tripMinIndex, tripMaxIndex):
                suitableTrips[index-1].display(index, len(suitableTrips))
            selection = self.tripSelectionMenu(tripMinIndex, tripMaxIndex, len(suitableTrips))
            if selection is None:
                if tripMaxIndex != len(suitableTrips)+1:
                    tripMinIndex = tripMaxIndex
                else:
                    tripMinIndex = 1
                    tripMaxIndex = -1
                continue
            elif type(selection) != int and selection == False:
                print("Your trip is discarded. Returning to main menu...")
                return None
            else:
                print(f'Trip {selection+1} selected.')
                self.parseAirlineCodes(suitableTrips[selection])
                return suitableTrips[selection]

    def tripSelectionMenu(self, tripMin, tripMax, tripsTotal):
        while True:
            options = [
                f"\n(Showing trips {tripMin}-{tripMax-1} out of {tripsTotal})",
                "- Press a trip number to select it.",
                "- Press Enter to display next trips.",
                "- Press * to return to main menu."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '':
                return None
            elif userInput == '*':
                return False
            else:
                try:
                    selectedTrip = int(userInput)
                    if selectedTrip not in range(1, tripMax):
                        raise ValueError
                    return selectedTrip-1
                except ValueError:
                    print("Invalid input. Please try again.")
    
    def parseAirlineCodes(self, trip):
        for flight in trip.flights:
            try:
                airline_ID = next(airline.airline_ID for airline in self.app.airlines if airline.airline_name == flight.airline_ID)
                flight.setAirlineCode(airline_ID)
            except StopIteration:
                print("A critical internal error occurred. Please refer to the developers, mentioning the error code \"airlineProgramDatabaseMismatch\". Terminating...")
                sys.exit(-1)

    def makeBooking(self, trip, userChoices, returnTrip):
        print("\nLet's make your booking!")

        if returnTrip is None:
            print("\nStep 1:\tSelect a fare for your trip.")
        else:
            print(f"\nStep 1.1:\tSelect a fare for your trip from {trip.flights[0].departure_airport_code} to {trip.flights[-1].arrival_airport_code}.")
        fareSelection = self.selectFare(trip)
        if fareSelection is None:
            print("Your trip is discarded. Returning to main menu...")
            return None

        returnFareSelection = None
        if returnTrip is not None:
            print(f"\nStep 1.2:\tSelect a fare for your trip from {returnTrip.flights[0].departure_airport_code} to {returnTrip.flights[-1].arrival_airport_code}.")
            returnFareSelection = self.selectFare(returnTrip)
            if returnFareSelection is None:
                print("Your trip is discarded. Returning to main menu...")
                return None
        
        print("\nStep 2:\tEnter passenger information.")

        availableAgePolicies = self.getAvailableAgePolicies(trip)
        returnAvailableAgePolicies = None
        if returnTrip is not None:
            returnAvailableAgePolicies = self.getAvailableAgePolicies(returnTrip)
        passengerInfo = self.enterPassengerInfo(userChoices)

        if passengerInfo is None:
            print("Your trip is discarded. Returning to main menu...")
            return None

        if returnTrip is None:
            print("\nStep 3:\tSelect seats.")
        else:
            print(f"\nStep 3.1:\tSelect seats for your trip from {trip.flights[0].departure_airport_code} to {trip.flights[-1].arrival_airport_code}.")
        seatSelection = self.selectSeats(trip, passengerInfo, fareSelection)
        if seatSelection is None:
            print("Your trip is discarded. Returning to main menu...")
            return None

        returnSeatSelection = None
        if returnTrip is not None:
            print(f"\nStep 3.2:\tSelect seats for your trip from {returnTrip.flights[0].departure_airport_code} to {returnTrip.flights[-1].arrival_airport_code}.")
            returnSeatSelection = self.selectSeats(returnTrip, passengerInfo, returnFareSelection)
            if returnSeatSelection is None:
                print("Your trip is discarded. Returning to main menu...")
                return None

        if returnTrip is None:
            print("\nStep 4:\tAdd luggage.")
        else:
            print(f"\nStep 4.1:\tAdd luggage for your trip from {trip.flights[0].departure_airport_code} to {trip.flights[-1].arrival_airport_code}.")
        luggageSelection = self.selectLuggage(trip, passengerInfo, fareSelection)
        if luggageSelection is None:
            print("Your trip is discarded. Returning to main menu...")
            return None
        
        returnLuggageSelection = None
        if returnTrip is not None:
            print(f"\nStep 4.2:\tAdd luggage for your trip from {returnTrip.flights[0].departure_airport_code} to {returnTrip.flights[-1].arrival_airport_code}.")
            returnLuggageSelection = self.selectLuggage(returnTrip, passengerInfo, returnFareSelection)
            if returnLuggageSelection is None:
                print("Your trip is discarded. Returning to main menu...")
                return None
        
        booking = self.createBooking(0, passengerInfo[0].passenger_ID)
        tickets, ticket_counter = self.createTickets(trip, fareSelection, passengerInfo, seatSelection, luggageSelection, booking, availableAgePolicies, 0)
        luggage = self.createLuggage(luggageSelection, tickets)

        returnTickets = None
        returnLuggage = None
        if returnTrip is not None:
            returnTickets, ticket_counter = self.createTickets(returnTrip, returnFareSelection, passengerInfo, returnSeatSelection, returnLuggageSelection, booking, returnAvailableAgePolicies, ticket_counter)
            returnLuggage = self.createLuggage(returnLuggageSelection, returnTickets)

        print("\nAlmost done! Here is a summary of your booking:")

        confirmation = self.displaySummary(trip, fareSelection, passengerInfo, seatSelection, luggageSelection, availableAgePolicies, returnTrip, returnFareSelection, returnSeatSelection, returnLuggageSelection, returnAvailableAgePolicies, booking)

        if not confirmation:
            print("Your trip is discarded. Returning to main menu...")
            return None


        saveComplete = self.saveToDatabase(passengerInfo, booking, tickets, seatSelection, luggage, returnTickets, returnSeatSelection, returnLuggage)
        if saveComplete:
            paymentComplete = self.completePayment()
            
            if paymentComplete:
                self.app.databaseService.commitChanges()
                print("You have successfully made your booking! Opening the booking confirmation...")
                self.openBookingConfirmation(booking, passengerInfo[0])
                return True
            else:
                print("Payment was cancelled. Your trip is discarded. Returning to main menu...")
                return self.app.databaseService.rollbackChanges()
        else:
            print("There was an error from our side. You were not charged. Please try again.")
            return False
    
    def selectFare(self, trip):
        availableFares = self.getAvailableFares(trip)
        
        for i in range(4):
            fare_name = availableFares[trip.flights[0]][i].fare_name
            fare_price = 0
            for flight in trip.flights:
                fare_price += availableFares[flight][i].fare_price_coefficient * flight.priceForPassengers
            print(f'\t{i+1}.\t{fare_name} -- {fare_price:.2f}€')
        fareSelection = self.fareSelectionMenu(availableFares)
        return fareSelection

    def getAvailableFares(self, trip):
        availableFares = {}
        for flight in trip.flights:
            availableFares[flight] = []
            fareData = self.app.databaseService.getAvailableFares(flight.airline_code)
            for datum in fareData:
                availableFares[flight].append(Fare(
                    datum[0],
                    datum[1],
                    datum[2].split('~'),
                    float(datum[3])
                ))
        return availableFares

    def fareSelectionMenu(self, availableFares):
        while True:
            options = [
                "- Press a fare number to select it.",
                "- Press ? to view the amenities of each fare.",
                "- Press * to return to main menu."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                print("Your trip is discarded. Returning to main menu...")
                return False
            elif userInput == '?':
                print()
                for flight in availableFares:
                    for fare in availableFares[flight]:
                        print(f"{fare.fare_name} amenities for flight {flight.departure_airport_code}-{flight.arrival_airport_code}")
                        for amenity in fare.amenities:
                            print(f"- {amenity}")
                        print()
            else:
                try:
                    selectedFare = int(userInput)
                    if selectedFare not in range(1, 5):
                        raise ValueError
                    return {x:availableFares[x][selectedFare-1] for x in availableFares}
                except ValueError:
                    print("Invalid input. Please try again.")

    def getAvailableAgePolicies(self, trip):
        availableAgePolicies = {}
        for flight in trip.flights:
            availableAgePolicies[flight] = []
            agePolicyData = self.app.databaseService.getAvailableAgePolicies(flight.airline_code)
            for datum in agePolicyData:
                availableAgePolicies[flight].append(AgePolicy(
                    datum[0],
                    int(datum[1]),
                    float(datum[2])
                ))
        return availableAgePolicies

    def enterPassengerInfo(self, userChoices):
        passengers = []
        ageCategories = [('Adult', 'passengersAdults'), ('Child', 'passengersChildren'), ('Infant', 'passengersInfants')]
        ageCategory = 0
        count = 1
        EMAIL_REGEX = re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")

        while True:
            if count >= userChoices[ageCategories[ageCategory][1]]+1:
                if ageCategory < 2:
                    ageCategory += 1
                    count = 1
                    continue
                else:
                    break
            while True:
                firstName = input(f'\n- {ageCategories[ageCategory][0]} {count}: First name: ').title()
                if firstName == '*': return None
                if not firstName.replace(' ','').isalpha() or len(firstName) < 2: print("Invalid first name entered. Must be alphabetic and have at least two characters.")
                else: break
            while True:
                lastName = input(f'- {ageCategories[ageCategory][0]} {count}: Last name: ').title()
                if lastName == '*': return None
                if not lastName.replace(' ','').isalpha() or len(lastName) < 2: print("Invalid last name entered. Must be alphabetic and have at least two characters.")
                else: break
            if ageCategory < 2:
                while True:
                    id = input(f'- {ageCategories[ageCategory][0]} {count}: Identity card or Passport number: ').upper()
                    if id == '*': return None
                    if not id.isalnum() or len(id) < 8 or len(id) > 9: print("Invalid Identity card or Passport number entered. Must be alpha-numeric and have eight or nine characters.")
                    elif not id[:2].isalpha(): print("Invalid Identity card or Passport number entered. The first two characters must be alphabetic.")
                    elif not id[2:].isdigit(): print("Invalid Identity card or Passport number entered. The last six or seven characters must be numeric.")
                    elif id in [item.passenger_ID for item in passengers]: print("The Identity card or Passport number must be unique.")
                    else: break
            else: id = passengers[count-1].passenger_ID + '_INF'
            while True:
                age = input(f'- {ageCategories[ageCategory][0]} {count}: Age: ')
                if age == '*': return None
                try:
                    age = int(age)
                    if age < 0 or age > 120: raise ValueError
                    elif ageCategory == 0 and (age < 12): raise IndexError
                    elif ageCategory == 1 and (age < 2 or age > 11): raise IndexError
                    elif ageCategory == 2 and (age > 1): raise IndexError
                    else: break
                except ValueError:
                    print("Invalid age entered. Must be numeric and between 0 and 120.")
                except IndexError:
                    print(f"The entered age does not match the age category \"{ageCategories[ageCategory][0]}\". Please try again. If you want to change your passenger selection, press * to start over.")
            if ageCategory == 0:
                while True:
                    phone_number = input(f'- Adult {count}: Phone number: ')
                    if phone_number == '*': return None
                    if len(phone_number) < 8 or len(phone_number) > 14 or not phone_number[1:].isdigit(): print("Invalid phone number entered. Must be numeric and have between 9 and 13 digits.")
                    else: break
                while True:
                    email = input(f'- Adult {count}: E-mail: ')
                    if phone_number == '*': return None
                    if not EMAIL_REGEX.match(email): print("Invalid e-mail entered. Please try again.")
                    else: break
            else:
                phone_number = None
                email = None

            if ageCategories[ageCategory][0] == 'Adult': maxAge = None
            elif ageCategories[ageCategory][0] == 'Child': maxAge = 12
            else: maxAge = 2
            
            passengers.append(Passenger(
                id,
                firstName,
                lastName,
                age,
                phone_number,
                email,
                ageCategory = ageCategories[ageCategory][0],
                ageCategoryMaxAge = maxAge
            ))

            count += 1
        return passengers

    def selectSeats(self, trip, passengerInfo, fareSelection):
        availableSeats = self.getAvailableSeats(trip)
        seatSelection = self.seatSelectionMenu(trip, availableSeats, passengerInfo, fareSelection)
        return seatSelection

    def getAvailableSeats(self, trip):
        availableSeats = {}
        for flight in trip.flights:
            availableSeats[flight] = []
            seatData = self.app.databaseService.getAvailableSeats(flight.flight_number, flight.departure_datetime.strftime('%Y-%m-%d'))
            for datum in seatData:
                availableSeats[flight].append(Seatmap(
                    None,
                    datum[0].lstrip('0'),
                    datum[1]
                ))
        return availableSeats

    def seatSelectionMenu(self, trip, availableSeats, passengerInfo, fareSelection):
        selected_seats = {}
        adultSeats = []
        for flight in trip.flights:
            selected_seats[flight] = {}
            print(f"\n\tAvailable seats for flight {flight.departure_airport_code}-{flight.arrival_airport_code}:")
            print("\tSeat\tClass")
            print("\t----\t-----")
            for seat in availableSeats[flight]:
                print(f'\t{seat.seat_number.rjust(3)}\t{seat.seat_class} Class')

            if fareSelection[flight].fare_name == 'Business' and 'Business' not in [seat.seat_class for seat in availableSeats[flight]]:
                print("\n\tThere are no available Business Class seats in this flight. Please change your fare selection or select a different flight.")
                return None
            
            for passenger in passengerInfo:
                if passenger.ageCategory == 'Infant':
                    print(f'\t{passenger.first_name} {passenger.last_name} is infant, so they will sit with an adult.')
                    selected_seats[flight][passenger] = adultSeats[0]
                    adultSeats.pop(0)
                    continue
                while True:
                    userInput = input(f'\tEnter seat number for {passenger.first_name} {passenger.last_name} for flight {flight.departure_airport_code}-{flight.arrival_airport_code}: ')
                    if userInput == '*': return None
                    try:
                        selected_seat = next(seat for seat in availableSeats[flight] if seat.seat_number == userInput)
                        if ((fareSelection[flight].fare_name == 'Business') and (selected_seat.seat_class != 'Business')) or ((fareSelection[flight].fare_name != 'Business') and (selected_seat.seat_class == 'Business')):
                            raise ValueError(f"\tThe selected seat class ({selected_seat.seat_class}) does not match with the selected fare ({fareSelection[flight].fare_name})")
                        newSeat = TakenSeat(
                            selected_seat.seat_number.zfill(3),
                            flight.flight_number,
                            flight.departure_datetime
                        )
                        selected_seats[flight][passenger] = newSeat
                        if passenger.ageCategory == 'Adult':
                            adultSeats.append(newSeat)
                        break
                    except StopIteration:
                        print("\tInvalid seat number. Please try again.")
                    except ValueError as e:
                        print(e.args[0])
                availableSeats[flight].remove(selected_seat)
        return selected_seats

    def selectLuggage(self, trip, passengerInfo, fareSelection):
        availableLuggageTypes = self.getAvailableLuggageTypes(trip)
        luggageSelection = self.luggageSelectionMenu(trip, availableLuggageTypes, passengerInfo, fareSelection)
        return luggageSelection

    def getAvailableLuggageTypes(self, trip):
        availableLuggageTypes = {}
        for flight in trip.flights:
            availableLuggageTypes[flight] = []
            luggageTypeData = self.app.databaseService.getLuggageTypes(flight.airline_code)
            for datum in luggageTypeData:
                availableLuggageTypes[flight].append(LuggageType(
                    datum[0],
                    int(datum[1]),
                    int(datum[2]),
                    datum[3]
                ))
        return availableLuggageTypes

    def luggageSelectionMenu(self, trip, availableLuggageTypes, passengerInfo, fareSelection):
        selected_luggage = {}
        for flight in trip.flights:
            selected_luggage[flight] = {}
            for passenger in passengerInfo:
                if passenger.ageCategory != 'Infant':
                    selected_luggage[flight][passenger] = []
            print(f"\n\tLuggage policy for flight {flight.departure_airport_code}-{flight.arrival_airport_code}, for fare {fareSelection[flight].fare_name}:")
            if "1 carry-on bag up to 8kg or 1 personal item" in fareSelection[flight].amenities or "1 carry-on bag up to 8kg and 1 personal item" in fareSelection[flight].amenities:
                print(f"\tYou have one free carry-on bag up to 8kg.")
                for passenger in passengerInfo:
                    if passenger.ageCategory != 'Infant':
                        selected_luggage[flight][passenger].append(LuggageType(flight.airline_code, 8, 0, 'Carry-on'))
            if "1 carry-on bag up to 13kg and 1 personal item" in fareSelection[flight].amenities:
                print(f"\tYou have one free carry-on bag up to 13kg.")
                for passenger in passengerInfo:
                    if passenger.ageCategory != 'Infant':
                        selected_luggage[flight][passenger].append(LuggageType(flight.airline_code, 13, 0, 'Carry-on'))
            if "1 checked baggage up to 23kg" in fareSelection[flight].amenities:
                print(f"\tYou have one free checked baggage up to 23kg.")
                for passenger in passengerInfo:
                    if passenger.ageCategory != 'Infant':
                        selected_luggage[flight][passenger].append(LuggageType(flight.airline_code, 23, 0, 'Checked'))
            if "2 checked baggage up to 32kg each" in fareSelection[flight].amenities:
                print(f"\tYou have two free checked baggage up to 32kg each.")
                for passenger in passengerInfo:
                    if passenger.ageCategory != 'Infant':
                        selected_luggage[flight][passenger].append(LuggageType(flight.airline_code, 32, 0, 'Checked'))
                        selected_luggage[flight][passenger].append(LuggageType(flight.airline_code, 32, 0, 'Checked'))

            print(f"\n\tExtra luggage costs for flight {flight.departure_airport_code}-{flight.arrival_airport_code}:")
            print(f"\t---------------------------------------")
            
            for luggageType in availableLuggageTypes[flight]:
                print(f"\t{luggageType.category} baggage up to {luggageType.weight}kg:\t{luggageType.cost}€")

        for passenger in passengerInfo:
            if passenger.ageCategory == 'Infant': continue
            for flight in trip.flights:
                print(f"\n\tDoes {passenger.first_name} {passenger.last_name} want extra luggage for flight {flight.departure_airport_code}-{flight.arrival_airport_code}?")
                print(f"\tEnter the desired luggage weight to add, or leave the field blank to continue.")
                while True:
                    userInput = input("\tYour choice: ")
                    if userInput == '*':
                        return None
                    if userInput == '':
                        break
                    else:
                        try:
                            numericUserInput = int(userInput)
                            if numericUserInput not in [item.weight for item in availableLuggageTypes[flight]]:
                                raise ValueError
                            if 'Carry-on' in [item.category for item in selected_luggage[flight][passenger] if item.weight == numericUserInput]:
                                raise IndexError("\tYou already have one carry-on bag selected. You cannot have more than one carry-on bag.")
                            if 'Checked' in [item.category for item in availableLuggageTypes[flight] if item.weight == numericUserInput] and len([item for item in selected_luggage[flight][passenger] if item.category == 'Checked']) == 5:
                                raise IndexError("\tYou cannot have more than five checked luggage pieces.")
                            selected_luggage[flight][passenger].append(next(item for item in availableLuggageTypes[flight] if item.weight == numericUserInput))
                            print(f"\tA {selected_luggage[flight][passenger][-1].weight}kg luggage piece was added for {passenger.first_name} {passenger.last_name} for {selected_luggage[flight][passenger][-1].cost}€.")
                        except ValueError:
                            print("\tInvalid luggage weight. Please try again.")
                        except IndexError as e:
                            print(e.args[0])
        return selected_luggage

    def createBooking(self, total_price, main_passenger_ID):
        timestamp = datetime.now()
        return Booking(
            timestamp.strftime('%Y%m%d%H%M%S%f'),
            timestamp,
            total_price,
            main_passenger_ID
        )

    def createTickets(self, trip, fareSelection, passengerInfo, seatSelection, luggageSelection, booking, agePolicies, cntr_offset):
        tickets = {}
        total_price = 0
        cntr = 1 + cntr_offset
        for flight in trip.flights:
            tickets[flight] = {}
            for passenger in passengerInfo:
                ticketPrice = self.app.databaseService.calculateTicketPrice(
                    passenger.ageCategoryMaxAge,
                    [item.weight for item in luggageSelection[flight][passenger] if item.cost != 0] if passenger in luggageSelection[flight] else [],
                    flight.flight_number,
                    flight.departure_datetime,
                    fareSelection[flight].fare_name
                )
                
                tickets[flight][passenger] = Ticket(
                    booking.booking_code + str(cntr).zfill(2),
                    ticketPrice,
                    seatSelection[flight][passenger].seat_number,
                    flight.flight_number,
                    flight.departure_datetime,
                    passenger.passenger_ID,
                    booking.booking_code,
                    fareSelection[flight].fare_name,
                    flight.airline_code
                )

                self.ticketGenerator.addNewTicket(
                    passenger,
                    flight,
                    seatSelection[flight][passenger],
                    tickets[flight][passenger]
                )

                total_price += ticketPrice
                cntr += 1
        booking.addToTotalPrice(total_price)
        return tickets, cntr-1
    
    def createLuggage(self, luggageSelection, tickets):
        luggage = []
        cntr = 1
        for flight in luggageSelection:
            for passenger in luggageSelection[flight]:
                for luggagePiece in luggageSelection[flight][passenger]:
                    luggage.append(Luggage(
                        tickets[flight][passenger].ticket_ID + str(cntr),
                        tickets[flight][passenger].ticket_ID,
                        flight.airline_code,
                        luggagePiece.weight
                    ))
                    cntr += 1
                cntr = 1
        return luggage

    def displaySummary(self, trip, fareSelection, passengerInfo, seatSelection, luggageSelection, agePolicies, returnTrip, returnFareSelection, returnSeatSelection, returnLuggageSelection, returnAgePolicies, booking):
        self.displayTrip(trip)
        self.displayFare(fareSelection, trip)
        self.displayPassengers(passengerInfo)
        self.displaySeats(seatSelection)
        self.displayLuggage(luggageSelection)

        if returnTrip is not None:
            self.displayTrip(returnTrip)
            self.displayFare(returnFareSelection, returnTrip)
            self.displaySeats(returnSeatSelection)
            self.displayLuggage(returnLuggageSelection)

        print(f'\nTotal price: {booking.total_price:.2f}€')
        
        while True:
            print("\nIs this information correct? Enter Yes to confirm, or No to cancel your booking and start over.")
            userInput = input("Your choice: ")
            if userInput in ["Yes", "yes", "YES", "Y", "y"]:
                return True
            elif userInput in ["No", "no", "NO", "N", "n"]:
                return False
            print("Invalid input. Please try again.")

    def displayTrip(self, trip):
        print(f"\nYour trip from {trip.flights[0].departure_airport_code} to {trip.flights[-1].arrival_airport_code}:")
        if len(trip.flights) == 1:
            print(f"Direct flight")
        elif len(trip.flights) == 2:
            print(f"One stop in {trip.flights[0].arrival_airport_code}")
        else:
            print(f"Two stops in {trip.flights[0].arrival_airport_code} and {trip.flights[1].arrival_airport_code}")
        
        print(f" - Departs at: {trip.flights[0].departure_datetime_local.strftime('%A, %d %B %Y %I:%M %p')} local time")
        print(f" - Arrives at: {trip.flights[-1].arrival_datetime_local.strftime('%A, %d %B %Y %I:%M %p')} local time")
        print(f" - Duration: {trip.totalDuration // 60}h {trip.totalDuration % 60}min")

        print(', '.join([f'{flight.flight_number} by {flight.airline_ID}' for flight in trip.flights]))

    def displayFare(self, fareSelection, trip):
        print(f"\nFare: {fareSelection[trip.flights[0]].fare_name}")

    def displayPassengers(self, passengerInfo):
        print(f"\nPassengers:")

        for passenger in passengerInfo:
            print(f"\n-\t{passenger.first_name} {passenger.last_name} ({passenger.ageCategory})")
            if passenger.ageCategory == 'Adult':
                print(f"\tIdentity card or Passport number: {passenger.passenger_ID}")
                print(f"\tAge: {passenger.age}")
                print(f"\tPhone number: {passenger.phone_number}")
                print(f"\tE-mail: {passenger.email}")
            elif passenger.ageCategory == 'Child':
                print(f"\tIdentity card or Passport number: {passenger.passenger_ID}")
                print(f"\tAge: {passenger.age}")
            else:
                print(f"\tAge: {passenger.age}")

    def displaySeats(self, seatSelection):
        for flight in seatSelection:
            if len(seatSelection) > 1:
                print(f"\nSelected {'seats' if len(seatSelection[flight]) > 1 else 'seat'} for flight {flight.departure_airport_code}-{flight.arrival_airport_code}:")
            else:
                print(f"\nSelected {'seats' if len(seatSelection[flight]) > 1 else 'seat'}:")
            for passenger in seatSelection[flight]:
                if passenger.ageCategory == 'Infant':
                    print(f"-\t{passenger.first_name} {passenger.last_name} is infant, so they will sit with an adult.")
                else:
                    print(f"-\t{passenger.first_name} {passenger.last_name}:\tSeat {seatSelection[flight][passenger].seat_number.lstrip('0').rjust(3)}")

    def displayLuggage(self, luggageSelection):
        for flight in luggageSelection:
            if len(luggageSelection) > 1:
                print(f"\nSelected luggage {'pieces' if len(luggageSelection[flight]) > 1 else 'piece'} for flight {flight.departure_airport_code}-{flight.arrival_airport_code}:")
            else:
                print(f"\nSelected luggage {'pieces' if len(luggageSelection[flight]) > 1 else 'piece'}:")

            if len(luggageSelection[flight]) == 1:
                for passenger in luggageSelection[flight]:
                    for luggagePiece in luggageSelection[flight][passenger]:
                        print(f"-\t1 {luggagePiece.category} luggage piece up to {luggagePiece.weight}kg - {luggagePiece.cost}€")
            else:
                for passenger in luggageSelection[flight]:
                    print(f'\n-\t{passenger.first_name} {passenger.last_name}:')
                    for luggagePiece in luggageSelection[flight][passenger]:
                        print(f"\t-\t1 {luggagePiece.category} luggage piece up to {luggagePiece.weight}kg - {luggagePiece.cost}€")

    def saveToDatabase(self, passengerInfo, booking, tickets, seatSelection, luggage, returnTickets, returnSeatSelection, returnLuggage):
        for passenger in passengerInfo:
            response = self.app.databaseService.savePassenger(passenger)
            if not response:
                return False

        response = self.app.databaseService.saveBooking(booking)
        if not response:
            return False
        
        for flight in seatSelection:
            for passenger in seatSelection[flight]:
                if passenger.ageCategory != 'Infant':
                    response = self.app.databaseService.saveTakenSeat(seatSelection[flight][passenger])
                if not response:
                    return False
        
        if returnSeatSelection is not None:
            for flight in returnSeatSelection:
                for passenger in returnSeatSelection[flight]:
                    if passenger.ageCategory != 'Infant':
                        response = self.app.databaseService.saveTakenSeat(returnSeatSelection[flight][passenger])
                    if not response:
                        return False
        
        for flight in tickets:
            for passenger in tickets[flight]:
                response = self.app.databaseService.saveTicket(tickets[flight][passenger])
                if not response:
                    return False

        if returnTickets is not None:
            for flight in returnTickets:
                for passenger in returnTickets[flight]:
                    response = self.app.databaseService.saveTicket(returnTickets[flight][passenger])
                    if not response:
                        return False
        
        for luggagePiece in luggage:
            response = self.app.databaseService.saveLuggage(luggagePiece)
            if not response:
                return False
        
        if returnLuggage is not None:
            for luggagePiece in returnLuggage:
                response = self.app.databaseService.saveLuggage(luggagePiece)
                if not response:
                    return False
        return True

    def completePayment(self):
        print("\nRedirecting to the bank environment...")

        # Redirecting here to the bank environment...

        print("\nPayment complete!")
        return True

    def openBookingConfirmation(self, booking, lead_passenger):
        self.ticketGenerator.saveFile(f'FlyNow Booking {booking.booking_code} Confirmation', lead_passenger.email, f'{lead_passenger.first_name} {lead_passenger.last_name}')

    def helpMenu(self):
        while True:
            options = [
                "\nHelp menu options:",
                "- Press 1 to view a list of available cities.",
                "- Press 2 to view a list of available countries.",
                "- Press 3 to view a list of available regions.",
                "- Press * to return to main menu."
            ]

            for option in options:
                print(option)
            userInput = input("Your choice: ")

            if userInput == '*':
                return
            else:
                try:
                    numericUserInput = int(userInput)

                    if numericUserInput == 1:
                        minIndex = 1
                        maxIndex = -1
                        while maxIndex != len(self.app.cities):
                            maxIndex = min(minIndex+200, len(self.app.cities))+1
                            print(", ".join(self.app.cities[minIndex-1:maxIndex]))
                            print(f"\nShowing cities {minIndex}-{maxIndex}.")
                            print("Press Enter to show more.")
                            userInput = input()

                            if userInput == '*':
                                break
                            if maxIndex != len(self.app.cities)+1:
                                minIndex = maxIndex
                                continue
                            else:
                                break
                    elif numericUserInput == 2:
                        print(", ".join(self.app.countries))
                    elif numericUserInput == 3:
                        print(", ".join(self.app.regions))
                    else:
                        raise ValueError
                except ValueError:
                    print("Invalid input. Please try again.")
