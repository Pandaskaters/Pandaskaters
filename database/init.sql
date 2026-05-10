-- ─────────────────────────────────────────────────────────────
-- PandaSkaters – Schema inicial (PostgreSQL)
-- ─────────────────────────────────────────────────────────────

-- Enums
CREATE TYPE user_role      AS ENUM ('passenger', 'driver', 'admin');
CREATE TYPE driver_status  AS ENUM ('pending', 'approved', 'rejected', 'suspended');
CREATE TYPE vehicle_type   AS ENUM ('economy', 'premium', 'moto');
CREATE TYPE ride_status    AS ENUM ('searching', 'assigned', 'driver_arriving', 'in_progress', 'completed', 'cancelled');
CREATE TYPE service_type   AS ENUM ('economy', 'premium', 'moto');

-- Users
CREATE TABLE users (
    id               SERIAL PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    email            VARCHAR(150) UNIQUE NOT NULL,
    phone            VARCHAR(20)  UNIQUE NOT NULL,
    hashed_password  VARCHAR(255) NOT NULL,
    role             user_role DEFAULT 'passenger' NOT NULL,
    photo_url        VARCHAR(500),
    is_active        BOOLEAN DEFAULT TRUE,
    is_verified      BOOLEAN DEFAULT FALSE,
    rating           FLOAT DEFAULT 5.0,
    total_rides      INTEGER DEFAULT 0,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ
);

-- Drivers
CREATE TABLE drivers (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    cedula           VARCHAR(20) UNIQUE NOT NULL,
    license_number   VARCHAR(50) NOT NULL,
    license_photo_url VARCHAR(500),
    status           driver_status DEFAULT 'pending',
    is_online        BOOLEAN DEFAULT FALSE,
    current_lat      FLOAT,
    current_lng      FLOAT,
    rating           FLOAT DEFAULT 5.0,
    total_rides      INTEGER DEFAULT 0,
    total_earnings   FLOAT DEFAULT 0.0,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ
);

-- Vehicles
CREATE TABLE vehicles (
    id           SERIAL PRIMARY KEY,
    driver_id    INTEGER REFERENCES drivers(id) ON DELETE CASCADE,
    plate        VARCHAR(20) UNIQUE NOT NULL,
    brand        VARCHAR(50) NOT NULL,
    model        VARCHAR(50) NOT NULL,
    year         INTEGER NOT NULL,
    color        VARCHAR(30) NOT NULL,
    vehicle_type vehicle_type NOT NULL,
    photo_url    VARCHAR(500),
    is_active    BOOLEAN DEFAULT TRUE
);

-- Rides
CREATE TABLE rides (
    id                    SERIAL PRIMARY KEY,
    passenger_id          INTEGER REFERENCES users(id),
    driver_id             INTEGER REFERENCES drivers(id),
    origin_address        VARCHAR(300) NOT NULL,
    origin_lat            FLOAT NOT NULL,
    origin_lng            FLOAT NOT NULL,
    destination_address   VARCHAR(300) NOT NULL,
    destination_lat       FLOAT NOT NULL,
    destination_lng       FLOAT NOT NULL,
    service_type          service_type DEFAULT 'economy',
    status                ride_status DEFAULT 'searching',
    estimated_distance_km FLOAT,
    estimated_duration_min FLOAT,
    estimated_fare        FLOAT,
    final_fare            FLOAT,
    notes                 TEXT,
    cancellation_reason   VARCHAR(200),
    requested_at          TIMESTAMPTZ DEFAULT NOW(),
    assigned_at           TIMESTAMPTZ,
    started_at            TIMESTAMPTZ,
    completed_at          TIMESTAMPTZ
);

-- Ride Ratings
CREATE TABLE ride_ratings (
    id                SERIAL PRIMARY KEY,
    ride_id           INTEGER UNIQUE REFERENCES rides(id) ON DELETE CASCADE,
    passenger_rating  FLOAT,
    driver_rating     FLOAT,
    passenger_comment TEXT,
    driver_comment    TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rides_passenger   ON rides(passenger_id);
CREATE INDEX idx_rides_driver      ON rides(driver_id);
CREATE INDEX idx_rides_status      ON rides(status);
CREATE INDEX idx_drivers_online    ON drivers(is_online);
CREATE INDEX idx_users_email       ON users(email);
