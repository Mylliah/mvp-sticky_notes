import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage: React.FC = () => {
  return (
    <div className="landingContainer">
      <header className="heroSection">
        <div className="heroContent">
          <h1 className="title">Bienvenue sur <br/>T-Note</h1>
          <p className="subtitle">
            Votre espace pour capturer, organiser et partager vos idées, où que vous soyez.
          </p>
          <Link to="/login" className="ctaButton">
            Commencer
          </Link>
        </div>
      </header>

      <main className="featuresSection">
        <h2 className="featuresTitle">Fonctionnalités Clés</h2>
        <div className="featuresGrid">
          <div className="featureCard">
            <div className="featureIcon">📝</div>
            <h3>Prise de Notes Intuitive</h3>
            <p>Créez et mettez en forme des notes simplement, comme des post-its numériques.</p>
          </div>
          <div className="featureCard">
            <div className="featureIcon">🤝</div>
            <h3>Partage Facile</h3>
            <p>Collaborez en temps réel en partageant vos notes avec vos contacts.</p>
          </div>
          <div className="featureCard">
            <div className="featureIcon">☁️</div>
            <h3>Accès sécurisé</h3>
            <p>Profitez d'un accès sécurisé à toutes vos notes.</p>
          </div>
        </div>
      </main>

      <section className="videoSection">
        <h2 className="videoTitle">Démonstration de la plateforme</h2>
        <div className="videoWrapper">
          <video controls width="100%">
            <p>Votre navigateur ne supporte pas la lecture de vidéos. Voici un lien pour la <a href="#">télécharger</a>.</p>
          </video>
        </div>
      </section>

      <section className="aboutSection">
        <h2 className="aboutTitle">À Propos de T-Note</h2>
        <p>
          T-Note est né d'un besoin simple : centraliser les idées éparpillées et faciliter la collaboration.
          Dans un monde où les informations fusent, nous avons voulu créer un havre de paix numérique pour vos pensées,
          un endroit où la simplicité d'un post-it rencontre la puissance du cloud pour que vous ne perdiez plus jamais une idée.
        </p>
      </section>

      <footer className="footer">
        <p>© 2025 T-Note. Tous droits réservés.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
