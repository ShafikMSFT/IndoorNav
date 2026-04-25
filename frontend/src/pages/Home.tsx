import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div style={{ padding: "2rem", maxWidth: 800, margin: "0 auto" }}>
      <h1>Indoor Navigation</h1>
      <p>Transform walkthrough videos into interactive indoor maps.</p>

      <nav style={{ marginTop: "2rem", display: "flex", gap: "1rem" }}>
        <Link to="/admin/upload">
          <button>Upload Video (Admin)</button>
        </Link>
      </nav>

      <section style={{ marginTop: "2rem" }}>
        <h2>Available Maps</h2>
        <p>No maps yet. Upload a walkthrough video to get started.</p>
      </section>
    </div>
  );
}
