import { useState, useCallback } from 'react';
import Toast, { ToastType, ToastAction } from './Toast';
import './Toast.css';

export interface ToastOptions {
  message: string;
  type?: ToastType;
  duration?: number;
  actions?: ToastAction[];
}

interface ToastItem extends ToastOptions {
  id: string;
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  // Cette fonction sera exposée via un hook personnalisé
  const addToast = useCallback((options: ToastOptions) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const newToast: ToastItem = { id, ...options };
    setToasts((prev) => [...prev, newToast]);
    return id;
  }, []);

  // Exposer addToast globalement pour l'utiliser depuis n'importe où
  if (typeof window !== 'undefined') {
    (window as any).__addToast = addToast;
  }

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          actions={toast.actions}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}

// Hook personnalisé pour utiliser les toasts
export function useToast() {
  const addToast = useCallback((options: ToastOptions) => {
    if (typeof window !== 'undefined' && (window as any).__addToast) {
      return (window as any).__addToast(options);
    }
    return null;
  }, []);

  return { addToast };
}
