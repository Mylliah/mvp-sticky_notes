import { useEffect, useState } from 'react';
import './Toast.css';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastAction {
  label: string;
  onClick: () => void;
}

export interface ToastProps {
  id: string;
  message: string;
  type?: ToastType;
  duration?: number;
  actions?: ToastAction[];
  onClose?: () => void;
}

export default function Toast({ 
  id, 
  message, 
  type = 'info', 
  duration = 5000, 
  actions,
  onClose 
}: ToastProps) {
  const [isRemoving, setIsRemoving] = useState(false);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setIsRemoving(true);
    setTimeout(() => {
      if (onClose) {
        onClose();
      }
    }, 300); // Durée de l'animation
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'warning':
        return '⚠';
      case 'info':
      default:
        return 'ℹ';
    }
  };

  return (
    <div className={`toast ${type} ${isRemoving ? 'removing' : ''}`}>
      <span className="toast-icon">{getIcon()}</span>
      <div className="toast-content">
        <div className="toast-message">{message}</div>
        {actions && actions.length > 0 && (
          <div className="toast-actions">
            {actions.map((action, index) => (
              <button
                key={index}
                className={`toast-btn ${index === 0 ? 'primary' : 'secondary'}`}
                onClick={() => {
                  action.onClick();
                  handleClose();
                }}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>
      <button className="toast-close" onClick={handleClose}>
        ×
      </button>
    </div>
  );
}
