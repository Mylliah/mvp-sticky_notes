import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';
import welcomeVideo from '../assets/Welcome_to_sticky-notes.mp4';

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
            <source src={welcomeVideo} type="video/mp4" />
            Votre navigateur ne supporte pas la balise vidéo.
          </video>
        </div>
      </section>

      <section className="aboutSection">
        <h2 className="aboutTitle">À Propos de T-Note</h2>
        <p>
          T-Note est né d'une frustration réelle : une directrice d'agence, débordée par la complexité 
          des outils de prise de notes existants sur internet, rêvait d'une solution aussi simple qu'un 
          post-it papier, mais avec la puissance du numérique. Trop de fonctionnalités inutiles, 
          trop de menus cachés, trop de temps perdu à chercher comment faire quelque chose de basique.
        </p>
        <p>
          Nous avons alors créé T-Note : un outil qui va droit à l'essentiel. Pas de courbe d'apprentissage, 
          pas de manuel de 50 pages. Juste vos idées, vos notes, accessibles en un clic. Simple, intuitif, 
          efficace. Parce qu'une bonne application ne devrait jamais être plus compliquée que le problème 
          qu'elle résout.
        </p>
      </section>

      <section className="authorSection">
        <h2 className="authorTitle">L'Auteur</h2>
        <p className="authorDescription">
          Projet développé par <strong>Mylliah</strong>, développeur passionné par la création d'outils 
          simples et efficaces pour améliorer la productivité au quotidien.
        </p>
        <div className="authorLinks">
          <a 
            href="https://www.linkedin.com/in/myriam-mezhoud" 
            target="_blank" 
            rel="noopener noreferrer"
            className="authorLink linkedinLink"
          >
            <span className="linkIcon">💼</span> LinkedIn
          </a>
          <a 
            href="https://github.com/Mylliah" 
            target="_blank" 
            rel="noopener noreferrer"
            className="authorLink githubLink"
          >
            <span className="linkIcon">💻</span> GitHub
          </a>
        </div>
      </section>

      <footer className="footer">
        <p>© 2025 T-Note. Tous droits réservés.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
