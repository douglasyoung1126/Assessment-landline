-- Stations: realistic Landline service locations
INSERT INTO stations (code, name, city, state, timezone) VALUES
    ('FTC', 'Fort Collins Transit Center', 'Fort Collins', 'CO', 'America/Denver'),
    ('DIA', 'Denver International Airport', 'Denver', 'CO', 'America/Denver'),
    ('DLH', 'Duluth International Airport', 'Duluth', 'MN', 'America/Chicago'),
    ('MSP', 'Minneapolis-St. Paul Airport', 'Minneapolis', 'MN', 'America/Chicago')
ON CONFLICT (code) DO NOTHING;

-- Routes (directed pairs — a round trip is two routes)
INSERT INTO routes (origin_id, destination_id, distance_miles)
SELECT o.id, d.id, dist
FROM (VALUES
    ('FTC', 'DIA', 90),
    ('DIA', 'FTC', 90),
    ('DLH', 'MSP', 155),
    ('MSP', 'DLH', 155)
) AS v(orig, dest, dist)
JOIN stations o ON o.code = v.orig
JOIN stations d ON d.code = v.dest
ON CONFLICT (origin_id, destination_id) DO NOTHING;

-- Schedules: Fort Collins ↔ Denver (2h trips, 9 departures each way)
INSERT INTO schedules (route_id, departure_time, arrival_time, days_of_week, valid_from)
SELECT r.id, dep::time, arr::time, 127, '2025-01-01'
FROM (VALUES
    ('FTC', 'DIA', '04:30', '06:30'),
    ('FTC', 'DIA', '06:00', '08:00'),
    ('FTC', 'DIA', '07:30', '09:30'),
    ('FTC', 'DIA', '09:00', '11:00'),
    ('FTC', 'DIA', '11:00', '13:00'),
    ('FTC', 'DIA', '13:00', '15:00'),
    ('FTC', 'DIA', '15:00', '17:00'),
    ('FTC', 'DIA', '17:00', '19:00'),
    ('FTC', 'DIA', '19:00', '21:00'),
    ('DIA', 'FTC', '08:30', '10:30'),
    ('DIA', 'FTC', '10:00', '12:00'),
    ('DIA', 'FTC', '11:30', '13:30'),
    ('DIA', 'FTC', '13:00', '15:00'),
    ('DIA', 'FTC', '15:00', '17:00'),
    ('DIA', 'FTC', '17:00', '19:00'),
    ('DIA', 'FTC', '19:00', '21:00'),
    ('DIA', 'FTC', '21:00', '23:00')
) AS v(orig, dest, dep, arr)
JOIN stations o ON o.code = v.orig
JOIN stations d ON d.code = v.dest
JOIN routes r ON r.origin_id = o.id AND r.destination_id = d.id;

-- Schedules: Duluth ↔ Minneapolis (2.5h trips, 5 departures each way)
INSERT INTO schedules (route_id, departure_time, arrival_time, days_of_week, valid_from)
SELECT r.id, dep::time, arr::time, 127, '2025-01-01'
FROM (VALUES
    ('DLH', 'MSP', '05:00', '07:30'),
    ('DLH', 'MSP', '08:00', '10:30'),
    ('DLH', 'MSP', '11:00', '13:30'),
    ('DLH', 'MSP', '14:00', '16:30'),
    ('DLH', 'MSP', '17:00', '19:30'),
    ('MSP', 'DLH', '09:00', '11:30'),
    ('MSP', 'DLH', '12:00', '14:30'),
    ('MSP', 'DLH', '15:00', '17:30'),
    ('MSP', 'DLH', '18:00', '20:30'),
    ('MSP', 'DLH', '21:00', '23:30')
) AS v(orig, dest, dep, arr)
JOIN stations o ON o.code = v.orig
JOIN stations d ON d.code = v.dest
JOIN routes r ON r.origin_id = o.id AND r.destination_id = d.id;

-- Fare rules: realistic Landline pricing (children ride free)
INSERT INTO fare_rules (route_id, passenger_type, price_cents, effective_from)
SELECT r.id, pt::passenger_type, cents, '2025-01-01'::date
FROM (VALUES
    ('FTC', 'DIA', 'adult', 2900),
    ('FTC', 'DIA', 'child', 0),
    ('DIA', 'FTC', 'adult', 2900),
    ('DIA', 'FTC', 'child', 0),
    ('DLH', 'MSP', 'adult', 3900),
    ('DLH', 'MSP', 'child', 0),
    ('MSP', 'DLH', 'adult', 3900),
    ('MSP', 'DLH', 'child', 0)
) AS v(orig, dest, pt, cents)
JOIN stations o ON o.code = v.orig
JOIN stations d ON d.code = v.dest
JOIN routes r ON r.origin_id = o.id AND r.destination_id = d.id
ON CONFLICT (route_id, passenger_type, effective_from) DO NOTHING;

-- Materialize trips for the next 180 days.
-- In production this would be a scheduled job; here we seed up-front.
INSERT INTO trips (schedule_id, date, total_seats, available_seats)
SELECT s.id, d::date, 56, 56
FROM schedules s
CROSS JOIN generate_series(CURRENT_DATE, CURRENT_DATE + INTERVAL '180 days', '1 day') d
WHERE s.is_active = true
  AND (s.days_of_week & (1 << EXTRACT(DOW FROM d::date)::int)) > 0
  AND d::date >= s.valid_from
  AND (s.valid_until IS NULL OR d::date <= s.valid_until)
ON CONFLICT (schedule_id, date) DO NOTHING;
