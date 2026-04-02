import type { Trip, SearchParams, Station } from "../types";

interface Props {
  trips: Trip[];
  searchParams: SearchParams;
  stations: Station[];
  onSelect: (trip: Trip) => void;
  onBack: () => void;
}

function dollars(cents: number) {
  return `$${(cents / 100).toFixed(2)}`;
}

export function TripResults({
  trips,
  searchParams,
  stations,
  onSelect,
  onBack,
}: Props) {
  const originStation = stations.find((s) => s.code === searchParams.origin);
  const destStation = stations.find(
    (s) => s.code === searchParams.destination,
  );

  const dateLabel = new Date(searchParams.date + "T00:00:00").toLocaleDateString(
    "en-US",
    { weekday: "long", month: "long", day: "numeric", year: "numeric" },
  );

  return (
    <div>
      <div className="results-header">
        <div>
          <h2>
            {originStation?.city ?? searchParams.origin} &rarr;{" "}
            {destStation?.city ?? searchParams.destination}
          </h2>
          <span style={{ color: "var(--text-light)" }}>{dateLabel}</span>
        </div>
        <button className="btn btn-outline" onClick={onBack}>
          &larr; Back
        </button>
      </div>

      {trips.length === 0 ? (
        <div className="no-trips">
          <p>No trips available for this date.</p>
          <p style={{ marginTop: "0.5rem" }}>
            Try a different date or route.
          </p>
        </div>
      ) : (
        <div className="trip-list">
          {trips.map((trip) => (
            <div key={trip.id} className="trip-card">
              <div>
                <div className="trip-times">
                  <span className="trip-time">{trip.departure_time}</span>
                  <span className="trip-arrow">&rarr;</span>
                  <span className="trip-time">{trip.arrival_time}</span>
                </div>
                <div className="trip-seats">
                  {trip.available_seats} seat
                  {trip.available_seats !== 1 && "s"} available
                </div>
              </div>

              <div className="trip-price">
                <div className="amount">
                  {dollars(trip.fares.adult_price_cents)}
                </div>
                <div className="label">per adult</div>
                {trip.fares.child_price_cents === 0 && (
                  <div className="label" style={{ color: "var(--success)" }}>
                    Kids ride free
                  </div>
                )}
              </div>

              <button
                className="btn btn-primary"
                onClick={() => onSelect(trip)}
              >
                Select
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
