import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { PublicLayout } from './components/layout/PublicLayout';

// Pages
import { LoginPage } from './pages/auth/LoginPage';
import { DashboardPage } from './pages/recruiter/DashboardPage';
import { JobsPage } from './pages/recruiter/JobsPage';
import { CandidatesPage } from './pages/recruiter/CandidatesPage';
import { PipelinePage } from './pages/recruiter/PipelinePage';
import { SearchPage } from './pages/recruiter/SearchPage';
import { AnalyticsPage } from './pages/recruiter/AnalyticsPage';
import { ActivityPage } from './pages/recruiter/ActivityPage';
import { CareersPage } from './pages/public/CareersPage';
import { JobDetailPage } from './pages/public/JobDetailPage';
import { LoadingSpinner } from './components/common/LoadingSpinner';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <LoadingSpinner message="Checking authentication session..." size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const RootRedirect: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/careers" replace />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Careers Routes */}
          <Route element={<PublicLayout />}>
            <Route path="/careers" element={<CareersPage />} />
            <Route path="/jobs/:slug" element={<JobDetailPage />} />
          </Route>

          {/* Authentication */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Recruiter ATS Suite */}
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/candidates" element={<CandidatesPage />} />
            <Route path="/pipeline" element={<PipelinePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/activity" element={<ActivityPage />} />
          </Route>

          {/* Default Root */}
          <Route path="/" element={<RootRedirect />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
