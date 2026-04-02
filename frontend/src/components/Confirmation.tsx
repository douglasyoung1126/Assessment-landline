import type { Reservation } from "../types";

interface Props {
  reservation: Reservation;
  onReset: () => void;
}

function dollars(cents: number) {
  return `$${(cents / 100).toFixed(2)}`;
}

export function Confirmation({ reservation, onReset }: Props) {
  const dateLabel = new Date(
    reservation.trip_date + "T00:00:00",
  ).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="confirmation">
      <div className="check">&check;</div>
      <h2>Booking Confirmed!</h2>
      <p style={{ color: "var(--text-light)" }}>
        A confirmation has been sent to {reservation.contact_email}
      </p>

      <div className="code">{reservation.confirmation_code}</div>

      <div className="confirmation-details">
        <div className="row">
          <span className="label">Route</span>
          <span>
            {reservation.origin} &rarr; {reservation.destination}
          </span>
        </div>
        <div className="row">
          <span className="label">Date</span>
          <span>{dateLabel}</span>
        </div>
        <div className="row">
          <span className="label">Time</span>
          <span>
            {reservation.departure_time} &ndash; {reservation.arrival_time}
          </span>
        </div>
        <div className="row">
          <span className="label">Passengers</span>
          <span>{reservation.passengers.length}</span>
        </div>

        {reservation.passengers.map((p, i) => (
          <div className="row" key={i}>
            <span className="label" style={{ paddingLeft: "1rem" }}>
              {p.first_name} {p.last_name}
            </span>
            <span>
              {p.passenger_type} &mdash; {dollars(p.price_cents)}
            </span>
          </div>
        ))}

        <div className="row">
          <span className="label">Total Paid</span>
          <span>{dollars(reservation.total_cents)}</span>
        </div>
      </div>

      <button
        className="btn btn-primary"
        onClick={onReset}
        style={{ marginTop: "1rem" }}
      >
        Book Another Trip
      </button>
    </div>
  );
}
