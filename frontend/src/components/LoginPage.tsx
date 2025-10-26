import { useState, FormEvent } from 'react';
import { authService } from '../services/auth.service';
import './LoginPage.css';

interface LoginPageProps {
  onLoginSuccess: () => void;
  onSwitchToRegister?: () => void;
}

export default function LoginPage({ onLoginSuccess, onSwitchToRegister }: LoginPageProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await authService.login({ email, password });
      onLoginSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de connexion');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <h1 className="login-title">📝 Sticky Notes</h1>
          <p className="login-subtitle">Connectez-vous pour accéder à vos notes</p>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="votre@email.com"
                disabled={isLoading}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Mot de passe</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>

            <div className="forgot-password-link">
              <button
                type="button"
                className="link-btn"
                onClick={() => alert('Fonctionnalité "Mot de passe oublié" à venir')}
              >
                Mot de passe oublié ?
              </button>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="login-btn"
              disabled={isLoading}
            >
              {isLoading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          <div className="login-help">
            <p>💡 Comptes de test :</p>
            <p><strong>Email:</strong> testuser1@test.com</p>
            <p><strong>Mot de passe:</strong> SecurePass123!</p>
            <p><strong>Email:</strong> saido@test.com</p>
            <p><strong>Mot de passe:</strong> azeqsdwxc</p>
            <p><strong>Email:</strong> MaoMao</p>
            <p><strong>Mot de passe:</strong> azeqsdwxc</p>
          </div>

          {onSwitchToRegister && (
            <div className="login-footer">
              <p>
                Pas encore de compte ?{' '}
                <button
                  type="button"
                  className="switch-link"
                  onClick={onSwitchToRegister}
                >
                  S'inscrire
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
