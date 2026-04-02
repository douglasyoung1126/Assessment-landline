import type {
  Station,
  Trip,
  SearchParams,
  ReservationCreate,
  Reservation,
} from "./types";

const API = "/api";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${url}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const fetchStations = () => request<Station[]>("/stations");

export const searchTrips = (p: SearchParams) =>
  request<Trip[]>(
    `/trips/search?origin=${encodeURIComponent(p.origin)}&destination=${encodeURIComponent(p.destination)}&date=${encodeURIComponent(p.date)}`,
  );

export const createReservation = (payload: ReservationCreate) =>
  request<Reservation>("/reservations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
