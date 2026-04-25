import { useParams } from "react-router-dom";

export default function MapEditor() {
  const { mapId } = useParams<{ mapId: string }>();

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Map Editor</h1>
      <p>Editing map: {mapId}</p>
      {/* TODO: Canvas-based graph editor for nodes, edges, POIs */}
      <div
        style={{
          marginTop: "1rem",
          width: "100%",
          height: "70vh",
          border: "2px dashed #ccc",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#999",
        }}
      >
        Graph editor canvas will render here
      </div>
    </div>
  );
}
