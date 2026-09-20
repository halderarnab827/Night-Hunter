import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import LandingPage from './components/LandingPage.jsx'

const isLocal =
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  window.location.hostname === '0.0.0.0';

function Root() {
  if (isLocal) {
    return window.location.pathname === '/landing' ? <LandingPage /> : <App />;
  }

  // On public website (Render): visitors cannot directly run the app online
  if (window.location.pathname === '/app') {
    window.location.replace('/#downloads');
    return null;
  }

  return <LandingPage />;
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)
