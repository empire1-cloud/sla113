import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AppHeader from "./components/AppHeader";
import SystemStatusBanner from "./components/SystemStatusBanner";
import SettingsSidebar from "./components/SettingsSidebar";
import { Toaster } from "./components/ui/sonner";

// Empire 1 Pages (routed universe)
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import OAuthCallbackPage from "./pages/OAuthCallbackPage";
import ProfilePage from "./pages/ProfilePage";
import TeamSettingsPage from "./pages/TeamSettingsPage";
import AcceptInvitePage from "./pages/AcceptInvitePage";
import BillingPage from "./pages/BillingPage";
import APIKeysPage from "./pages/APIKeysPage";
import AdminOverviewPage from "./pages/AdminOverviewPage";
import EnginesPage from "./pages/EnginesPage";
import MoneyPipelinePage from "./pages/MoneyPipelinePage";
import PipelineComposerPage from "./pages/PipelineComposerPage";
import ExecutionHistoryPage from "./pages/ExecutionHistoryPage";
import AnalyticsPage from "./pages/AnalyticsPage";

// SLA113 — parent factory layer
import SLA113App from "./sla113/SLA113App";

/**
 * Root Router — SLA113 is parent, Empire is a routed universe.
 * /sla113/* and / -> SLA113App
 * /empire/* and legacy empire paths -> Empire shell
 */
function RootRouter() {
  const location = useLocation();
  const path = location.pathname;
  const legacyEmpirePaths = [
    "/login",
    "/signup",
    "/forgot-password",
    "/reset-password",
    "/oauth/callback",
    "/invite/accept",
    "/engines",
    "/money-pipeline",
    "/pipeline-composer",
    "/history",
    "/analytics",
    "/profile",
    "/team/settings",
    "/billing",
    "/settings/api-keys",
    "/admin/overview",
  ];
  const isEmpireUniverse =
    path.startsWith("/empire") || legacyEmpirePaths.some((legacyPath) => path.startsWith(legacyPath));

  if (!isEmpireUniverse) {
    return <SLA113App />;
  }

  const normalizeEmpirePath = (routePath) => routePath.replace(/^\/empire/, "") || "/";

  return (
    <AuthProvider>
      <AppHeader />
      <SystemStatusBanner />
      <div className="app-layout">
        <SettingsSidebar />
        <main className="app-main">
          <Routes>
            {/* Public */}
            <Route path={normalizeEmpirePath("/login")} element={<LoginPage />} />
            <Route path={normalizeEmpirePath("/signup")} element={<SignupPage />} />
            <Route path={normalizeEmpirePath("/forgot-password")} element={<ForgotPasswordPage />} />
            <Route path={normalizeEmpirePath("/reset-password")} element={<ResetPasswordPage />} />
            <Route path={normalizeEmpirePath("/oauth/callback")} element={<OAuthCallbackPage />} />
            <Route path={normalizeEmpirePath("/invite/accept")} element={<AcceptInvitePage />} />

            {/* Protected */}
            <Route path={normalizeEmpirePath("/")} element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/engines")} element={<ProtectedRoute><EnginesPage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/money-pipeline")} element={<ProtectedRoute><MoneyPipelinePage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/pipeline-composer")} element={<ProtectedRoute><PipelineComposerPage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/history")} element={<ProtectedRoute><ExecutionHistoryPage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/analytics")} element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/profile")} element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/team/settings")} element={<ProtectedRoute><TeamSettingsPage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/billing")} element={<ProtectedRoute><BillingPage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/settings/api-keys")} element={<ProtectedRoute><APIKeysPage /></ProtectedRoute>} />
            <Route path={normalizeEmpirePath("/admin/overview")} element={<ProtectedRoute><AdminOverviewPage /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to={normalizeEmpirePath("/")} replace />} />
          </Routes>
        </main>
      </div>
      <Toaster richColors position="top-right" />
    </AuthProvider>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/empire/*" element={<RootRouter />} />
          <Route path="*" element={<RootRouter />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
