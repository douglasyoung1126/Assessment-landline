# Landline Shuttle Booking System

A production-minded shuttle booking prototype for [Landline](https://landline.com) — premium motorcoach service connecting cities to major airports.

## Quick Start

```bash
docker-compose up --build
```

Then open **http://localhost:3000** in your browser.

| Service  | URL                    | Purpose                        |
|----------|------------------------|--------------------------------|
| Frontend | http://localhost:3000   | React booking UI               |
| Backend  | http://localhost:8000   | FastAPI REST API               |
| Postgres | localhost:5432         | Database (user/pass: landline) |

To tear down and reset:

```bash
docker-compose down -v
```

## Testing the Flow

### Via the UI

1. Open http://localhost:3000
2. Select an origin (e.g. Fort Collins, CO), destination (e.g. Denver, CO), and a date
3. Pick a trip from the results
4. Enter passenger details and submit
5. See the confirmation with your booking code

### Via the API

```bash
# List stations
curl http://localhost:8000/api/stations

# Search trips
curl "http://localhost:8000/api/trips/search?origin=FTC&destination=DIA&date=2026-04-15"

# Book a trip (use a trip ID from the search results)
curl -X POST http://localhost:8000/api/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": 1,
    "contact_email": "test@example.com",
    "contact_phone": "555-123-4567",
    "passengers": [
      {"first_name": "Jane", "last_name": "Doe", "passenger_type": "adult"},
      {"first_name": "Sam",  "last_name": "Doe", "passenger_type": "child"}
    ]
  }'

# Look up a reservation
curl http://localhost:8000/api/reservations/LND-XXXXXX

# Cancel a reservation
curl -X POST http://localhost:8000/api/reservations/LND-XXXXXX/cancel
```

## Project Structure

```
.
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── migrate.py                  # Forward-only migration runner
│   ├── migrations/
│   │   ├── 001_schema.sql          # Tables, types, indexes, constraints
│   │   └── 002_seed.sql            # Stations, routes, schedules, fares, trips
│   └── app/
│       ├── main.py                 # FastAPI app + lifespan
│       ├── config.py               # Environment-based settings
│       ├── database.py             # Async connection pool
│       ├── schemas.py              # Pydantic request models
│       ├── routers/
│       │   ├── health.py           # Liveness + readiness probes
│       │   ├── stations.py         # GET /api/stations
│       │   ├── trips.py            # GET /api/trips/search
│       │   └── reservations.py     # POST/GET reservations + cancel
│       └── services/
│           └── booking.py          # Booking logic with concurrency control
└── frontend/
    ├── Dockerfile                  # Multi-stage: build → nginx
    ├── nginx.conf                  # Reverse proxy /api → backend
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx                 # Step-based flow controller
        ├── App.css                 # Full stylesheet
        ├── api.ts                  # Fetch wrapper
        ├── types.ts                # TypeScript interfaces
        └── components/
            ├── SearchForm.tsx      # Origin / Destination / Date
            ├── TripResults.tsx     # Available trip listing
            ├── BookingForm.tsx     # Passenger details + submit
            └── Confirmation.tsx    # Booking confirmation
```

## Seed Data

Realistic routes based on Landline's actual service areas:

| Route                                 | Price (adult) | Duration | Daily Departures |
|---------------------------------------|---------------|----------|------------------|
| Fort Collins, CO → Denver Airport     | $29.00        | 2h       | 9                |
| Denver Airport → Fort Collins, CO     | $29.00        | 2h       | 8                |
| Duluth, MN → Minneapolis Airport      | $39.00        | 2.5h     | 5                |
| Minneapolis Airport → Duluth, MN      | $39.00        | 2.5h     | 5                |

Children 12 & under ride free on all routes. Trips are materialized 180 days out.

---


## AI Tools Used

I used **Cursor IDE** (Claude) for:

- Drafting the architecture document and evaluating design trade-offs
- Scaffolding the FastAPI backend, React frontend, and Docker configuration
- Generating seed data SQL with realistic Landline route/schedule information
- Writing the concurrency-controlled booking service

All AI output was reviewed and iterated on for correctness, consistency with the architecture, and production readiness.
