import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Login from './pages/Login';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Narration from './pages/Narration';
import Dictation from './pages/Dictation';
import Flashcard from './pages/Flashcard';
import Review from './pages/Review';
import Layout from './components/Layout';
import './index.css';

import { ErrorBoundary } from './components/ErrorBoundary';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { DataProvider } from './contexts/DataContext';

function ProtectedRoute() {
  const { session, loading } = useAuth();
  
  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Loading...</div>;
  }
  
  if (!session) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <DataProvider>
          <Router>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              
              <Route element={<ProtectedRoute />}>
                <Route element={<Layout />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/narration/:courseId" element={<Narration />} />
                  <Route path="/dictation/:courseId" element={<Dictation />} />
                  <Route path="/flashcard/:courseId" element={<Flashcard />} />
                  <Route path="/course/:courseId/review" element={<Review />} />
                </Route>
              </Route>
            </Routes>
          </Router>
        </DataProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
