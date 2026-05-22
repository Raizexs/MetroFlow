import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { fetchStatus } from "./api/client";
import { AppShell } from "./components/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { PrivacyPage } from "./pages/PrivacyPage";

export default function App() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    fetchStatus()
      .then(() => {
        setApiOnline(true);
        setApiError(null);
      })
      .catch(() => {
        setApiOnline(false);
        setApiError(
          "No se pudo conectar al backend. Verifique VITE_API_URL en Vercel o ejecute uvicorn en local.",
        );
      });
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell apiOnline={apiOnline} />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/vagones" element={<DashboardPage />} />
          <Route path="/privacidad" element={<PrivacyPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>

      {apiError && (
        <div className="fixed bottom-4 left-1/2 z-50 max-w-md -translate-x-1/2 rounded-xl border border-red-500/40 bg-red-950/90 px-4 py-3 text-center text-sm text-red-200 shadow-xl">
          {apiError}
        </div>
      )}
    </BrowserRouter>
  );
}
