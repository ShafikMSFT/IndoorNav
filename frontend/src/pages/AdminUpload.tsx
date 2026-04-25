import { useState, useCallback } from "react";

export default function AdminUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/videos/upload", {
      method: "POST",
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      setStatus(`Uploaded! Video ID: ${data.video_id} — Status: ${data.status}`);
    } else {
      setStatus(`Upload failed: ${res.statusText}`);
    }
  }, [file]);

  return (
    <div style={{ padding: "2rem", maxWidth: 600, margin: "0 auto" }}>
      <h1>Upload Walkthrough Video</h1>
      <p>Upload a video of the indoor space to generate a navigable map.</p>

      <div style={{ marginTop: "1.5rem" }}>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </div>

      <button
        onClick={handleUpload}
        disabled={!file}
        style={{ marginTop: "1rem" }}
      >
        Upload & Process
      </button>

      {status && <p style={{ marginTop: "1rem" }}>{status}</p>}
    </div>
  );
}
