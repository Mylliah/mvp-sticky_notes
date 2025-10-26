import React from 'react';
import './SkeletonCard.css';

/**
 * Composant placeholder pour afficher un squelette de carte pendant le chargement
 */
export default function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-header">
        <div className="skeleton-title"></div>
        <div className="skeleton-actions"></div>
      </div>
      <div className="skeleton-content">
        <div className="skeleton-line"></div>
        <div className="skeleton-line"></div>
        <div className="skeleton-line short"></div>
      </div>
      <div className="skeleton-footer">
        <div className="skeleton-badge"></div>
        <div className="skeleton-badge"></div>
      </div>
    </div>
  );
}
