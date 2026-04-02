CREATE TYPE trip_status AS ENUM ('scheduled', 'cancelled', 'completed');
CREATE TYPE reservation_status AS ENUM ('confirmed', 'cancelled');
CREATE TYPE passenger_type AS ENUM ('adult', 'child');

CREATE TABLE stations (
    id SERIAL PRIMARY KEY,
    code VARCHAR(5) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/Denver'
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    origin_id INTEGER NOT NULL REFERENCES stations(id),
    destination_id INTEGER NOT NULL REFERENCES stations(id),
    distance_miles INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    UNIQUE(origin_id, destination_id)
);

CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES routes(id),
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    days_of_week SMALLINT NOT NULL DEFAULT 127,
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_until DATE,
    is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE fare_rules (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES routes(id),
    passenger_type passenger_type NOT NULL DEFAULT 'adult',
    price_cents INTEGER NOT NULL,
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_until DATE,
    UNIQUE(route_id, passenger_type, effective_from)
);

CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL REFERENCES schedules(id),
    date DATE NOT NULL,
    total_seats INTEGER NOT NULL DEFAULT 56,
    available_seats INTEGER NOT NULL DEFAULT 56,
    status trip_status NOT NULL DEFAULT 'scheduled',
    version INTEGER NOT NULL DEFAULT 1,
    UNIQUE(schedule_id, date),
    CHECK (available_seats >= 0),
    CHECK (available_seats <= total_seats)
);

CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id),
    confirmation_code VARCHAR(10) NOT NULL UNIQUE,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20),
    total_cents INTEGER NOT NULL,
    seat_count INTEGER NOT NULL,
    status reservation_status NOT NULL DEFAULT 'confirmed',
    booked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    cancelled_at TIMESTAMPTZ,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE passengers (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    passenger_type passenger_type NOT NULL DEFAULT 'adult',
    price_cents INTEGER NOT NULL
);

CREATE UNIQUE INDEX idx_trips_schedule_date ON trips(schedule_id, date);
CREATE INDEX idx_trips_availability ON trips(date, status) INCLUDE (available_seats);
CREATE INDEX idx_reservations_confirmation ON reservations(confirmation_code);
CREATE INDEX idx_reservations_email ON reservations(contact_email);
CREATE INDEX idx_schedules_route ON schedules(route_id) WHERE is_active = true;
