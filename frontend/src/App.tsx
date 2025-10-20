// Premier composant React
// C'est comme une fonction Python qui retourne du HTML

function App() {
  // Cette fonction retourne du JSX (HTML dans du JavaScript)
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>🎉 Bienvenue sur Sticky Notes !</h1>
      <p>Application de notes prête</p>
      
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <h2>✅ Ce qui fonctionne :</h2>
        <ul>
          <li>React installé</li>
          <li>Vite tourne dans Docker</li>
          <li>Ce composant s'affiche</li>
        </ul>
      </div>

      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '8px' }}>
        <h2>🎯 Prochaines étapes :</h2>
        <ul>
          <li>Créer la page de connexion</li>
          <li>Afficher la liste des notes</li>
          <li>Se connecter à l'API Flask</li>
        </ul>
      </div>
    </div>
  )
}

// exporte le composant pour pouvoir l'utiliser ailleurs
export default App
