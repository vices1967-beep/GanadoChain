// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
// Cambia esta línea:
// import "./index.css";
// Por esta:
import './assets/styles/global.scss'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)