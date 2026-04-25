import { useParams } from "react-router-dom";
import { useState } from "react";

export default function Navigate() {
  const { mapId } = useParams<{ mapId: string }>();
  const [destination, setDestination] = useState("");

  return (
    <div style={{ padding: "2rem", maxWidth: 600, margin: "0 auto" }}>
      <h1>Navigate</h1>
      <p>Map: {mapId}</p>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Where do you want to go?</h2>
        <input
          type="text"
          placeholder="e.g. 'Dr. Smith's office' or 'the kitchen'"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
        />
        <button style={{ marginTop: "0.5rem" }}>Find Route</button>
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>Camera View</h2>
        {/* TODO: Camera feed with AR overlay for navigation */}
        <div
          style={{
            width: "100%",
            height: "50vh",
            background: "#111",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#666",
            borderRadius: "8px",
          }}
        >
          Camera feed will appear here
        </div>
      </section>
    </div>
  );
}
