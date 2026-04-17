import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ErrorBoundary from "./components/ErrorBoundary";
import Dashboard from "./pages/Dashboard";
import LiveMonitor from "./pages/LiveMonitor";
import Students from "./pages/Students";
import Attendance from "./pages/Attendance";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import { useAuthStore } from "./store/authStore";

function ProtectedLayout({ children }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return (
    <div className="flex h-screen bg-slate-100">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <ErrorBoundary>{children}</ErrorBoundary>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/"          element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/live"      element={<ProtectedLayout><LiveMonitor /></ProtectedLayout>} />
      <Route path="/students"  element={<ProtectedLayout><Students /></ProtectedLayout>} />
      <Route path="/attendance"element={<ProtectedLayout><Attendance /></ProtectedLayout>} />
      <Route path="/reports"   element={<ProtectedLayout><Reports /></ProtectedLayout>} />
      <Route path="/settings"  element={<ProtectedLayout><Settings /></ProtectedLayout>} />
      <Route path="*"          element={<Navigate to="/" replace />} />
    </Routes>
  );
}
