import { useState, useEffect } from 'react'
import NotesPage from './NotesPage'
import LoginPage from './components/LoginPage'
import RegisterPage from './components/RegisterPage'
import { authService } from './services/auth.service'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showRegister, setShowRegister] = useState(false)

  useEffect(() => {
    // Vérifier si l'utilisateur est déjà connecté
    setIsAuthenticated(authService.isAuthenticated())
  }, [])

  const handleLoginSuccess = () => {
    setIsAuthenticated(true)
    setShowRegister(false)
  }

  const handleRegisterSuccess = () => {
    setIsAuthenticated(true)
    setShowRegister(false)
  }

  const handleLogout = () => {
    authService.logout()
    setIsAuthenticated(false)
  }

  if (!isAuthenticated) {
    if (showRegister) {
      return (
        <RegisterPage 
          onRegisterSuccess={handleRegisterSuccess}
          onSwitchToLogin={() => setShowRegister(false)}
        />
      )
    }
    return (
      <LoginPage 
        onLoginSuccess={handleLoginSuccess}
        onSwitchToRegister={() => setShowRegister(true)}
      />
    )
  }

  return <NotesPage onLogout={handleLogout} />
}

export default App
