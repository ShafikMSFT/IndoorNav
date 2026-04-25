import { Routes, Route } from "react-router-dom";
import { useIsAuthenticated, useMsal } from "@azure/msal-react";
import Home from "./pages/Home";
import AdminUpload from "./pages/AdminUpload";
import MapEditor from "./pages/MapEditor";
import Navigate from "./pages/Navigate";

function AuthButton() {
  const isAuthenticated = useIsAuthenticated();
  const { instance } = useMsal();

  if (isAuthenticated) {
    return (
      <button onClick={() => instance.logoutPopup()}>Sign out</button>
    );
  }
  return (
    <button onClick={() => instance.loginPopup()}>Sign in</button>
  );
}

export default function App() {
  return (
    <>
      <header style={{ padding: "0.5rem 1rem", borderBottom: "1px solid #eee", display: "flex", justifyContent: "flex-end" }}>
        <AuthButton />
      </header>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/admin/upload" element={<AdminUpload />} />
        <Route path="/admin/maps/:mapId/edit" element={<MapEditor />} />
        <Route path="/navigate/:mapId" element={<Navigate />} />
      </Routes>
    </>
  );
}
