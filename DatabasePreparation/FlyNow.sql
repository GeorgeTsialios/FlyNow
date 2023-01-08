BEGIN TRANSACTION;

DROP TABLE IF EXISTS "AIRCRAFT";
CREATE TABLE IF NOT EXISTS "AIRCRAFT"
(
	"aircraft_type"		varchar(30)		NOT NULL,

	PRIMARY KEY("aircraft_type")
);

DROP TABLE IF EXISTS "SEAT_MAP";
CREATE TABLE IF NOT EXISTS "SEAT_MAP"
(
	"aircraft_type"		varchar(30)		NOT NULL,
	"seat_number"		varchar(4)		NOT NULL,
	"seat_class"		varchar(30)		DEFAULT 'ECONOMY',

	PRIMARY KEY("aircraft_type","seat_number"),
	FOREIGN KEY ("aircraft_type") REFERENCES "AIRCRAFT"("aircraft_type") ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS "TAKEN_SEAT";
CREATE TABLE IF NOT EXISTS "TAKEN_SEAT"
(
	"seat_number"		varchar(4)		NOT NULL,
	"flight_number"		varchar(10)		NOT NULL,
	"departure_datetime"	datetime		NOT NULL,

	PRIMARY KEY ("seat_number","flight_number","departure_datetime"),
	FOREIGN KEY ("flight_number","departure_datetime") REFERENCES "FLIGHT"("flight_number","departure_datetime") ON DELETE CASCADE ON UPDATE CASCADE
);


DROP TABLE IF EXISTS "PASSENGER";
CREATE TABLE IF NOT EXISTS "PASSENGER"
(
	"passenger_ID"	varchar(20)		NOT NULL,
	"first_name"	varchar(20)		NOT NULL,
	"last_name"		varchar(20)		NOT NULL,
	"age"			smallint		NOT NULL,
	"phone_number"	varchar(20)		DEFAULT '',
	"email"		varchar(20)		NOT NULL,

	PRIMARY KEY ("passenger_ID"),
	CONSTRAINT "Valid_Age" CHECK ("age" > 0)
);

DROP TABLE IF EXISTS "LOCATION";
CREATE TABLE IF NOT EXISTS "LOCATION"
(
	"country"		varchar(30)		NOT NULL,
	"city"		varchar(30)		NOT NULL,
	"region"		varchar(30)		DEFAULT '',
	"time_zone"		varchar(50)		DEFAULT '',
	
	PRIMARY KEY ("country","city")
);

DROP TABLE IF EXISTS "AIRPORT";
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

DROP TABLE IF EXISTS "FLIGHT";
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


DROP TABLE IF EXISTS "TICKET";
CREATE TABLE IF NOT EXISTS "TICKET"
(
	"ticket_ID"			varchar(20)		NOT NULL,
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


DROP TABLE IF EXISTS "BOOKING";
CREATE TABLE IF NOT EXISTS "BOOKING"
(
	"booking_code"		varchar(20)		NOT NULL,
	"booking_date"		date			DEFAULT NULL,
	"total_price"		decimal(8,2)	NOT NULL,
	"main_passenger_ID"	varchar(20)		NOT NULL	DEFAULT '0',

	PRIMARY KEY ("booking_code"),
	FOREIGN KEY ("main_passenger_ID") REFERENCES "PASSENGER"("passenger_ID") ON DELETE SET DEFAULT ON UPDATE CASCADE
);

DROP TABLE IF EXISTS "AGE_POLICY";
CREATE TABLE IF NOT EXISTS "AGE_POLICY"
(
	"airline_ID"			char(3)		NOT NULL,
	"max_age"				smallint		NOT NULL,
	"age_price_coefficient"		decimal(3,2)	DEFAULT '1',

	PRIMARY KEY ("airline_ID", "max_age"),
	FOREIGN KEY ("airline_ID") REFERENCES "AIRLINE"("airline_ID") ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT "Valid_Max_Age" CHECK("max_age" > 0)
);


DROP TABLE IF EXISTS "AIRLINE";
CREATE TABLE IF NOT EXISTS "AIRLINE"
(
	"airline_ID"	char(3)		NOT NULL,
	"airline_name"	varchar(30)		DEFAULT '',

	PRIMARY KEY ("airline_ID")
	CONSTRAINT "Valid_Airline_ID" CHECK (length("airline_ID") = 3)
);


DROP TABLE IF EXISTS "FARE";
CREATE TABLE IF NOT EXISTS "FARE"
(
	"fare_name"				varchar(30)		NOT NULL,
	"airline_ID"			char(3)		NOT NULL,
	"amenities"				varchar(100)	DEFAULT '',
	"fare_price_coefficient"	decimal(3,2)	DEFAULT '1',

	PRIMARY KEY("fare_name","airline_ID"),
	FOREIGN KEY ("airline_ID") REFERENCES "AIRLINE"("airline_ID") ON DELETE CASCADE ON UPDATE CASCADE		
);


DROP TABLE IF EXISTS "LUGGAGE_TYPE";
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


DROP TABLE IF EXISTS "LUGGAGE";
CREATE TABLE IF NOT EXISTS "LUGGAGE"
(
	"luggage_ID"	varchar(20)		NOT NULL,
	"ticket_ID"		varchar(20)		NOT NULL,
	"airline_ID"	char(3)		NOT NULL,
	"weight"		smallint		NOT NULL,

	PRIMARY KEY("luggage_ID")
	FOREIGN KEY("ticket_ID") REFERENCES "TICKET"("ticket_ID")	ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ("airline_ID","weight") REFERENCES "LUGGAGE_TYPE"("airline_ID","weight") ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE INDEX IF NOT EXISTS "idx_FLIGHT" ON "FLIGHT"(departure_airport_code);
CREATE INDEX IF NOT EXISTS "idx_AIRPORT" ON "AIRPORT"(city);
CREATE INDEX IF NOT EXISTS "idx_TAKEN_SEAT" ON "TAKEN_SEAT"(flight_number);	


END TRANSACTION;