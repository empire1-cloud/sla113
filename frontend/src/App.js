import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AppHeader from "./components/AppHeader";

// Pages
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

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <AppHeader />
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
            <Route path="/invite/accept" element={<AcceptInvitePage />} />
            
            {/* Protected routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            } />
            <Route path="/engines" element={
              <ProtectedRoute>
                <EnginesPage />
              </ProtectedRoute>
            } />
            <Route path="/money-pipeline" element={
              <ProtectedRoute>
                <MoneyPipelinePage />
              </ProtectedRoute>
            } />
            <Route path="/pipeline-composer" element={
              <ProtectedRoute>
                <PipelineComposerPage />
              </ProtectedRoute>
            } />
            <Route path="/history" element={
              <ProtectedRoute>
                <ExecutionHistoryPage />
              </ProtectedRoute>
            } />
            <Route path="/analytics" element={
              <ProtectedRoute>
                <AnalyticsPage />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
            <Route path="/team/settings" element={
              <ProtectedRoute>
                <TeamSettingsPage />
              </ProtectedRoute>
            } />
            <Route path="/billing" element={
              <ProtectedRoute>
                <BillingPage />
              </ProtectedRoute>
            } />
            <Route path="/settings/api-keys" element={
              <ProtectedRoute>
                <APIKeysPage />
              </ProtectedRoute>
            } />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
