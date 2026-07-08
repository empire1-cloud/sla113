import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AppHeader from "./components/AppHeader";
import SystemStatusBanner from "./components/SystemStatusBanner";
import SettingsSidebar from "./components/SettingsSidebar";
import { Toaster } from "./components/ui/sonner";

// Empire 1 Pages
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
import EmpireLyricMasterPage from "./pages/EmpireLyricMasterPage";

// SLA113 — Fully isolated sovereign OS (separate project/repo)
// SLA113 runs on its own domain/port — NOT embedded in Empire 1
import SLA113App from "./sla113/SLA113App";
import ArcadePage from "./arcade/ArcadePage";
import ShowcasePage from "./pages/ShowcasePage";

/**
 * Root Router — splits traffic at the top level.
 * /sla113/* → SLA113App (isolated, no Empire 1 providers)
 * /arcade    → Public Arcade Portal (no auth)
 * /showcase  → Public Investor Showcase (no auth)
 * Everything else → Empire 1 (AuthProvider, AppHeader, etc.)
 */
function RootRouter() {
  const location = useLocation();
  const isSLA113 = location.pathname.startsWith("/sla113");
  const isArcade = location.pathname.startsWith("/arcade");
  const isShowcase = location.pathname.startsWith("/showcase");

  if (isSLA113) {
    return <SLA113App />;
  }
  if (isArcade) {
    return <ArcadePage />;
  }
  if (isShowcase) {
    return <ShowcasePage />;
  }

  return (
    <AuthProvider>
      <AppHeader />
      <SystemStatusBanner />
      <div className="app-layout">
        <SettingsSidebar />
        <main className="app-main">
          <Routes>
            {/* Public */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
            <Route path="/invite/accept" element={<AcceptInvitePage />} />

            {/* Protected */}
            <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
            <Route path="/empire" element={<ProtectedRoute><EmpireLyricMasterPage /></ProtectedRoute>} />
            <Route path="/engines" element={<ProtectedRoute><EnginesPage /></ProtectedRoute>} />
            <Route path="/money-pipeline" element={<ProtectedRoute><MoneyPipelinePage /></ProtectedRoute>} />
            <Route path="/pipeline-composer" element={<ProtectedRoute><PipelineComposerPage /></ProtectedRoute>} />
            <Route path="/history" element={<ProtectedRoute><ExecutionHistoryPage /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path="/team/settings" element={<ProtectedRoute><TeamSettingsPage /></ProtectedRoute>} />
            <Route path="/billing" element={<ProtectedRoute><BillingPage /></ProtectedRoute>} />
            <Route path="/settings/api-keys" element={<ProtectedRoute><APIKeysPage /></ProtectedRoute>} />
            <Route path="/admin/overview" element={<ProtectedRoute><AdminOverviewPage /></ProtectedRoute>} />
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
        <RootRouter />
      </BrowserRouter>
    </div>
  );
}

export default App;
