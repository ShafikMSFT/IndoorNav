import { useState, useCallback, useRef, useEffect, DragEvent } from "react";
import { useApi } from "../hooks/useApi";

interface VideoStatus {
  video_id: string;
  status: string;
  frames_extracted: number;
  error?: string;
}

export default function AdminUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [videoStatus, setVideoStatus] = useState<VideoStatus | null>(null);
  const [error, setError] = useState<string>("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const { apiFetch } = useApi();

  // Poll processing status
  useEffect(() => {
    if (!videoStatus || videoStatus.status === "completed" || videoStatus.status === "failed") {
      if (pollRef.current) clearInterval(pollRef.current);
      return;
    }
    pollRef.current = setInterval(async () => {
      try {
        const res = await apiFetch(`/api/videos/${videoStatus.video_id}/status`);
        if (res.ok) {
          const data: VideoStatus = await res.json();
          setVideoStatus(data);
          if (data.status === "completed" || data.status === "failed") {
            if (pollRef.current) clearInterval(pollRef.current);
          }
        }
      } catch { /* keep polling */ }
    }, 3000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [videoStatus?.video_id, videoStatus?.status]);

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    setVideoStatus(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await apiFetch("/api/videos/upload", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setVideoStatus({ video_id: data.video_id, status: data.status, frames_extracted: 0 });
        setFile(null);
      } else {
        const body = await res.text();
        setError(`Upload failed: ${res.status} ${body}`);
      }
    } catch (err) {
      setError(`Upload failed: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setUploading(false);
    }
  }, [file, apiFetch]);

  const onDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.type.startsWith("video/")) {
      setFile(droppedFile);
      setError("");
    } else {
      setError("Please drop a video file.");
    }
  }, []);

  const statusColor = videoStatus?.status === "completed" ? "#4caf50"
    : videoStatus?.status === "failed" ? "#f44336"
    : "#2196f3";

  return (
    <div style={{ padding: "2rem", maxWidth: 600, margin: "0 auto" }}>
      <h1>Upload Walkthrough Video</h1>
      <p>Upload a video of the indoor space to generate a navigable map.</p>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        style={{
          marginTop: "1.5rem",
          padding: "2rem",
          border: `2px dashed ${dragOver ? "#2196f3" : "#ccc"}`,
          borderRadius: 8,
          textAlign: "center",
          backgroundColor: dragOver ? "#e3f2fd" : "#fafafa",
          cursor: "pointer",
          transition: "all 0.2s",
        }}
        onClick={() => document.getElementById("file-input")?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept="video/*"
          style={{ display: "none" }}
          onChange={(e) => {
            setFile(e.target.files?.[0] ?? null);
            setError("");
          }}
        />
        {file ? (
          <p><strong>{file.name}</strong> ({(file.size / 1024 / 1024).toFixed(1)} MB)</p>
        ) : (
          <p>Drag & drop a video here, or click to browse</p>
        )}
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        style={{
          marginTop: "1rem",
          padding: "0.6rem 1.5rem",
          fontSize: "1rem",
          cursor: file && !uploading ? "pointer" : "not-allowed",
        }}
      >
        {uploading ? "Uploading..." : "Upload & Process"}
      </button>

      {error && <p style={{ marginTop: "1rem", color: "#f44336" }}>{error}</p>}

      {videoStatus && (
        <div style={{ marginTop: "1.5rem", padding: "1rem", border: "1px solid #ddd", borderRadius: 8 }}>
          <p><strong>Video ID:</strong> {videoStatus.video_id}</p>
          <p>
            <strong>Status:</strong>{" "}
            <span style={{ color: statusColor, fontWeight: 600 }}>{videoStatus.status}</span>
          </p>
          <p><strong>Frames extracted:</strong> {videoStatus.frames_extracted}</p>
          {videoStatus.error && <p style={{ color: "#f44336" }}>{videoStatus.error}</p>}
          {videoStatus.status !== "completed" && videoStatus.status !== "failed" && (
            <p style={{ fontSize: "0.85rem", color: "#888" }}>Polling every 3s...</p>
          )}
        </div>
      )}
    </div>
  );
}
