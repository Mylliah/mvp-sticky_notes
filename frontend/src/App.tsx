import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import NotesPage from './NotesPage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import LandingPage from './components/LandingPage';
import { authService } from './services/auth.service';
import './App.css';

const HomeRedirect = () => {
  const isAuthenticated = authService.isAuthenticated();
  return isAuthenticated ? <Navigate to="/notes" replace /> : <LandingPage />;
};

const App = () => {
  return (
      <Routes>
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route 
          path="/notes" 
          element={
            <ProtectedRoute>
              <Notes />
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
  );
};

const Login = () => {
  const navigate = useNavigate();
  return <LoginPage onLoginSuccess={() => navigate('/notes')} onSwitchToRegister={() => navigate('/register')} />;
};

const Register = () => {
  const navigate = useNavigate();
  return <RegisterPage onRegisterSuccess={() => navigate('/notes')} onSwitchToLogin={() => navigate('/login')} />;
};

const Notes = () => {
  const navigate = useNavigate();
  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };
  return <NotesPage onLogout={handleLogout} />;
};

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const isAuthenticated = authService.isAuthenticated();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default App;
