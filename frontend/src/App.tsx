import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

function authed() {
  return !!localStorage.getItem("token");
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={authed() ? <Dashboard /> : <Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

      </Routes>
    </BrowserRouter>
  );
}