import { useState, useEffect } from 'react'
import NotesPage from './NotesPage'
import LoginPage from './components/LoginPage'
import { authService } from './services/auth.service'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Vérifier si l'utilisateur est déjà connecté
    setIsAuthenticated(authService.isAuthenticated())
  }, [])

  const handleLoginSuccess = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    authService.logout()
    setIsAuthenticated(false)
  }

  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />
  }

  return <NotesPage onLogout={handleLogout} />
}

export default App
