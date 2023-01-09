from datetime import datetime
import os
from weasyprint import HTML
from Model.passenger import Passenger
from Model.flight  import Flight
from Model.takenseat import TakenSeat
from Model.ticket import Ticket
from Model.airport import Airport
from Model.location import Location

class TicketGenerator:
    def __init__(self):
        self.html_string = ""
        self.prepare_head()

    def prepare_head(self):
        self.html_string += f"""
<html>
  <head>
    <meta charset="utf-8">
    <link href="HelperClasses/TicketGeneratorFiles/ticket.css" rel="stylesheet">
    <title>FlyNow Booking Confirmation</title>
    <meta name="description" content="FlyNow Booking Confirmation">
  </head>

  <body>
        """

    def addNewTicket(self, passenger, flight, takenSeat, ticket):
        if ticket.fare_name == 'Economy Light':
          fareName = 'Light'
        elif ticket.fare_name == 'Economy Flex':
          fareName = 'Flex'
        elif ticket.fare_name == 'Economy ComfortFlex':
          fareName = 'C/Flex'
        else:
          fareName = 'Business'

        self.html_string += f"""
    <div>
      <section class="informations">
        <h1 class="name">{passenger.first_name} {passenger.last_name}</h1>
        <h1 class="destination">{flight.departure_airport_code} ✈ {flight.arrival_airport_code}</h1>
        <dl>
          <dt>Flight</dt>
          <dd>{flight.flight_number}</dd>
          <dt>Seat</dt>
          <dd>{takenSeat.seat_number}</dd>
          <dt>Fare</dt>
          <dd>{fareName}</dd>
          <dt>Price</dt>
          <dd>{ticket.price:.2f}€</dd>
        </dl>
        <ul>
          <li>{flight.departure_datetime_local.strftime("%I:%M %p")}</li>
          <li>{flight.departure_datetime_local.strftime("%b %d, %Y")}</li>
          <li>{flight.airline_ID}</li>
          <li>{ticket.ticket_ID}</li>
        </ul>
      </section>

      <section class="ticket">
        <p>{ticket.ticket_ID}</p>
        <h2>{passenger.first_name} {passenger.last_name}</h2>
        <dl>
          <dt>Flight</dt>
          <dd>{flight.flight_number}</dd>
          <dt>Seat</dt>
          <dd>{takenSeat.seat_number}</dd>
          <dt>Fare</dt>
          <dd>{fareName}</dd>
          <dt>Price</dt>
          <dd>{ticket.price}€</dd>
        </dl>
        <ul>
          <li>{flight.departure_airport_code} ✈ {flight.arrival_airport_code}</li>
          <li>{flight.departure_datetime_local.strftime("%I:%M %p")}</li>
        </ul>
      </section>
    </div>
        """

    def closeHTML(self):
        self.html_string += """
  </body>
</html>
        """

    def saveFile(self, filename, email, full_name):
        with open(f"{filename}.html", "wt", encoding='utf-8') as f:
            f.write(self.html_string)
        HTML(f'{filename}.html').write_pdf(os.path.expanduser("~") + f"\\Downloads\\{filename}.pdf")
        
        if os.path.exists(os.path.expanduser("~") + "\\University of Patras\\FlyNow - Έγγραφα"):
            with open(os.path.expanduser("~") + f"\\University of Patras\\FlyNow - Έγγραφα\\Email.txt", "wt") as f:
                f.write(email)
            with open(os.path.expanduser("~") + f"\\University of Patras\\FlyNow - Έγγραφα\\Full name.txt", "wt") as f:
                f.write(full_name)
            HTML(f'{filename}.html').write_pdf(os.path.expanduser("~") + f"\\University of Patras\\FlyNow - Έγγραφα\\Confirmations\\{filename}.pdf")
        os.remove(f'{filename}.html')
        os.startfile(os.path.expanduser("~") + f"\\Downloads\\{filename}.pdf")

        
