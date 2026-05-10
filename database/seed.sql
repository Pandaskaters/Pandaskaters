-- ─────────────────────────────────────────────────────────────
-- PandaSkaters – Datos de prueba
-- Contraseñas: demo123 (bcrypt hash incluido)
-- ─────────────────────────────────────────────────────────────

-- Admin (password: admin123)
INSERT INTO users (name, email, phone, hashed_password, role, is_active, is_verified)
VALUES (
    'Admin Sistema', 'admin@pandaskaters.com', '0000000000',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/4y1WbkL4gQ2TYVH0G',
    'admin', TRUE, TRUE
);

-- Demo Pasajero (password: demo123)
INSERT INTO users (name, email, phone, hashed_password, role, is_active, is_verified, rating, total_rides)
VALUES (
    'Ana González', 'passenger@demo.com', '0991234567',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'passenger', TRUE, TRUE, 4.8, 12
);

-- Demo Conductor (password: demo123)
INSERT INTO users (name, email, phone, hashed_password, role, is_active, is_verified, rating, total_rides)
VALUES (
    'Carlos Mendoza', 'driver@demo.com', '0987654321',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'driver', TRUE, TRUE, 4.9, 87
);

-- Driver profile
INSERT INTO drivers (user_id, cedula, license_number, status, is_online, current_lat, current_lng, rating, total_rides, total_earnings)
SELECT id, '1234567890', 'LIC-001234', 'approved', FALSE, 4.711, -74.072, 4.9, 87, 652.40
FROM users WHERE email = 'driver@demo.com';

-- Vehicle
INSERT INTO vehicles (driver_id, plate, brand, model, year, color, vehicle_type)
SELECT d.id, 'ABC-1234', 'Toyota', 'Corolla', 2021, 'Blanco', 'economy'
FROM drivers d JOIN users u ON d.user_id = u.id WHERE u.email = 'driver@demo.com';

-- Sample completed rides
INSERT INTO rides (passenger_id, driver_id, origin_address, origin_lat, origin_lng, destination_address, destination_lat, destination_lng, service_type, status, estimated_distance_km, estimated_duration_min, estimated_fare, final_fare, requested_at, completed_at)
SELECT
    p.id, d.id,
    'Av. El Dorado, Bogotá', 4.7110, -74.0721,
    'Centro Comercial Andino, Bogotá', 4.6666, -74.0530,
    'economy', 'completed', 5.2, 18.0, 7.16, 7.16,
    NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '25 min'
FROM users p, drivers d
JOIN users u ON d.user_id = u.id
WHERE p.email = 'passenger@demo.com' AND u.email = 'driver@demo.com';

INSERT INTO rides (passenger_id, driver_id, origin_address, origin_lat, origin_lng, destination_address, destination_lat, destination_lng, service_type, status, estimated_distance_km, estimated_duration_min, estimated_fare, final_fare, requested_at, completed_at)
SELECT
    p.id, d.id,
    'Aeropuerto El Dorado, Bogotá', 4.7016, -74.1469,
    'Hotel Tequendama, Bogotá', 4.6097, -74.0817,
    'premium', 'completed', 12.4, 35.0, 23.60, 23.60,
    NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '42 min'
FROM users p, drivers d
JOIN users u ON d.user_id = u.id
WHERE p.email = 'passenger@demo.com' AND u.email = 'driver@demo.com';
