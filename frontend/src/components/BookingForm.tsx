import { useState } from "react";
import type { Trip, PassengerInput, ReservationCreate } from "../types";

interface Props {
  trip: Trip;
  onBook: (payload: ReservationCreate) => void;
  onBack: () => void;
  loading: boolean;
}

function dollars(cents: number) {
  return `$${(cents / 100).toFixed(2)}`;
}

const blankPassenger = (): PassengerInput => ({
  first_name: "",
  last_name: "",
  passenger_type: "adult",
});

export function BookingForm({ trip, onBook, onBack, loading }: Props) {
  const [passengers, setPassengers] = useState<PassengerInput[]>([
    blankPassenger(),
  ]);
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const update = (idx: number, patch: Partial<PassengerInput>) =>
    setPassengers((prev) =>
      prev.map((p, i) => (i === idx ? { ...p, ...patch } : p)),
    );

  const addPassenger = () => {
    if (passengers.length < trip.available_seats) {
      setPassengers((prev) => [...prev, blankPassenger()]);
    }
  };

  const removePassenger = (idx: number) => {
    if (passengers.length > 1) {
      setPassengers((prev) => prev.filter((_, i) => i !== idx));
    }
  };

  const total = passengers.reduce(
    (sum, p) =>
      sum +
      (p.passenger_type === "child"
        ? trip.fares.child_price_cents
        : trip.fares.adult_price_cents),
    0,
  );

  const valid =
    email.trim() !== "" &&
    passengers.every((p) => p.first_name.trim() && p.last_name.trim());

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!valid) return;
    onBook({
      trip_id: trip.id,
      contact_email: email,
      contact_phone: phone || undefined,
      passengers,
    });
  };

  const dateLabel = new Date(trip.date + "T00:00:00").toLocaleDateString(
    "en-US",
    { weekday: "short", month: "short", day: "numeric" },
  );

  return (
    <div className="booking-section">
      <button
        className="btn btn-outline"
        onClick={onBack}
        style={{ marginBottom: "1rem" }}
      >
        &larr; Back to results
      </button>

      <div className="trip-summary">
        <h3>Selected Trip</h3>
        <div className="route">
          {trip.origin.city} &rarr; {trip.destination.city}
        </div>
        <div className="details">
          {dateLabel} &middot; {trip.departure_time} &ndash; {trip.arrival_time}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-card">
          <h3>Passengers</h3>

          {passengers.map((p, i) => (
            <div key={i} className="passenger-entry">
              <div className="passenger-header">
                <span>Passenger {i + 1}</span>
                {passengers.length > 1 && (
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() => removePassenger(i)}
                  >
                    Remove
                  </button>
                )}
              </div>
              <div className="passenger-fields">
                <div className="field">
                  <label>First Name</label>
                  <input
                    type="text"
                    value={p.first_name}
                    onChange={(e) =>
                      update(i, { first_name: e.target.value })
                    }
                    required
                  />
                </div>
                <div className="field">
                  <label>Last Name</label>
                  <input
                    type="text"
                    value={p.last_name}
                    onChange={(e) =>
                      update(i, { last_name: e.target.value })
                    }
                    required
                  />
                </div>
                <div className="field">
                  <label>Type</label>
                  <select
                    value={p.passenger_type}
                    onChange={(e) =>
                      update(i, {
                        passenger_type: e.target.value as "adult" | "child",
                      })
                    }
                  >
                    <option value="adult">Adult</option>
                    <option value="child">Child (12 &amp; under)</option>
                  </select>
                </div>
              </div>
            </div>
          ))}

          {passengers.length < trip.available_seats && (
            <button
              type="button"
              className="btn btn-outline btn-add"
              onClick={addPassenger}
            >
              + Add Passenger
            </button>
          )}
        </div>

        <div className="form-card">
          <h3>Contact Information</h3>
          <div className="contact-fields">
            <div className="field">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="field">
              <label>Phone (optional)</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="(555) 123-4567"
              />
            </div>
          </div>
        </div>

        <div className="total-bar">
          <span>Total</span>
          <span className="amount">{dollars(total)}</span>
        </div>

        <div className="booking-actions">
          <button type="button" className="btn btn-outline" onClick={onBack}>
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !valid}
          >
            {loading ? "Booking\u2026" : "Confirm Booking"}
          </button>
        </div>
      </form>
    </div>
  );
}
