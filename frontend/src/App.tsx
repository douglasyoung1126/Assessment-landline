import { useState, useEffect } from "react";
import { SearchForm } from "./components/SearchForm";
import { TripResults } from "./components/TripResults";
import { BookingForm } from "./components/BookingForm";
import { Confirmation } from "./components/Confirmation";
import { fetchStations, searchTrips, createReservation } from "./api";
import type {
  Station,
  Trip,
  Reservation,
  SearchParams,
  ReservationCreate,
} from "./types";
import "./App.css";

type Step = "search" | "results" | "booking" | "confirmation";

export default function App() {
  const [step, setStep] = useState<Step>("search");
  const [stations, setStations] = useState<Station[]>([]);
  const [searchParams, setSearchParams] = useState<SearchParams | null>(null);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);
  const [confirmation, setConfirmation] = useState<Reservation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStations().then(setStations).catch(console.error);
  }, []);

  const handleSearch = async (params: SearchParams) => {
    setLoading(true);
    setError(null);
    try {
      const results = await searchTrips(params);
      setSearchParams(params);
      setTrips(results);
      setStep("results");
    } catch {
      setError("Failed to search trips. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTrip = (trip: Trip) => {
    setSelectedTrip(trip);
    setError(null);
    setStep("booking");
  };

  const handleBook = async (payload: ReservationCreate) => {
    setLoading(true);
    setError(null);
    try {
      const result = await createReservation(payload);
      setConfirmation(result);
      setStep("confirmation");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Booking failed. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep("search");
    setSearchParams(null);
    setTrips([]);
    setSelectedTrip(null);
    setConfirmation(null);
    setError(null);
  };

  return (
    <div className="app">
      <header>
        <h1>Landline</h1>
        <span>Shuttle Booking</span>
      </header>

      <div className="container">
        {error && <div className="error-msg">{error}</div>}

        {step === "search" && (
          <SearchForm
            stations={stations}
            onSearch={handleSearch}
            loading={loading}
          />
        )}

        {step === "results" && searchParams && (
          <TripResults
            trips={trips}
            searchParams={searchParams}
            stations={stations}
            onSelect={handleSelectTrip}
            onBack={() => setStep("search")}
          />
        )}

        {step === "booking" && selectedTrip && (
          <BookingForm
            trip={selectedTrip}
            onBook={handleBook}
            onBack={() => setStep("results")}
            loading={loading}
          />
        )}

        {step === "confirmation" && confirmation && (
          <Confirmation reservation={confirmation} onReset={handleReset} />
        )}
      </div>
    </div>
  );
}
