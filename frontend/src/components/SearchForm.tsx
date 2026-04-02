import { useState } from "react";
import type { Station, SearchParams } from "../types";

interface Props {
  stations: Station[];
  onSearch: (params: SearchParams) => void;
  loading: boolean;
}

export function SearchForm({ stations, onSearch, loading }: Props) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState("");

  const today = new Date().toISOString().split("T")[0];
  const filteredDestinations = stations.filter((s) => s.code !== origin);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (origin && destination && date) {
      onSearch({ origin, destination, date });
    }
  };

  return (
    <div className="search-section">
      <h2>Book Your Shuttle</h2>
      <p>Premium motorcoach service connecting you to major airports</p>

      <form className="search-form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="origin">From</label>
          <select
            id="origin"
            value={origin}
            onChange={(e) => {
              setOrigin(e.target.value);
              if (e.target.value === destination) setDestination("");
            }}
            required
          >
            <option value="">Select origin</option>
            {stations.map((s) => (
              <option key={s.code} value={s.code}>
                {s.city}, {s.state}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="destination">To</label>
          <select
            id="destination"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
          >
            <option value="">Select destination</option>
            {filteredDestinations.map((s) => (
              <option key={s.code} value={s.code}>
                {s.city}, {s.state}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="date">Date</label>
          <input
            id="date"
            type="date"
            value={date}
            min={today}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>

        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Searching\u2026" : "Search"}
        </button>
      </form>
    </div>
  );
}
