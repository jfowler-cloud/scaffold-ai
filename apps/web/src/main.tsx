import React from 'react'
import ReactDOM from 'react-dom/client'
import '@cloudscape-design/global-styles/index.css'
import './index.css'
import { configureAmplify } from '@/lib/amplify'
import App from './App'

configureAmplify()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
