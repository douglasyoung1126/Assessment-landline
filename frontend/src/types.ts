export interface Station {
  id: number;
  code: string;
  name: string;
  city: string;
  state: string;
}

export interface Fares {
  adult_price_cents: number;
  child_price_cents: number;
}

export interface Trip {
  id: number;
  date: string;
  departure_time: string;
  arrival_time: string;
  origin: Station;
  destination: Station;
  available_seats: number;
  fares: Fares;
}

export interface SearchParams {
  origin: string;
  destination: string;
  date: string;
}

export interface PassengerInput {
  first_name: string;
  last_name: string;
  passenger_type: "adult" | "child";
}

export interface ReservationCreate {
  trip_id: number;
  contact_email: string;
  contact_phone?: string;
  passengers: PassengerInput[];
}

export interface PassengerDetail {
  first_name: string;
  last_name: string;
  passenger_type: string;
  price_cents: number;
}

export interface Reservation {
  confirmation_code: string;
  status: string;
  trip_date: string;
  departure_time: string;
  arrival_time: string;
  origin: string;
  destination: string;
  contact_email: string;
  contact_phone: string | null;
  passengers: PassengerDetail[];
  total_cents: number;
  booked_at: string;
}
