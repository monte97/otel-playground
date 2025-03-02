import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Faro SDK imports
import { initializeFaro } from '@grafana/faro-web-sdk';
import { getWebInstrumentations } from '@grafana/faro-web-sdk';

initializeFaro({
  url: 'http://192.168.0.138:4318/v1/traces', // Replace with your OTel Collector endpoint
  app: {
    name: 'my-react-app',
    version: '1.0.0',
    environment: 'development',
  },
  instrumentations: [
    ...getWebInstrumentations(),
  ],
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
