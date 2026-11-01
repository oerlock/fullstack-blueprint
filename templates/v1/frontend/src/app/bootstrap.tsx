import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../assets/styles/index.css'
import { config } from '../config'
import { AppProviders } from './providers/AppProviders'
import App from './App'

export function bootstrap(): void {
  document.title = config.appName

  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <AppProviders>
        <App />
      </AppProviders>
    </StrictMode>,
  )
}
