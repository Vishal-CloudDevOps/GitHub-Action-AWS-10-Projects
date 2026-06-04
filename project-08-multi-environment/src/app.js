const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

const ENV = process.env.NODE_ENV || 'development';
const VERSION = process.env.APP_VERSION || '1.0.0';
const FEATURE_FLAG = process.env.FEATURE_NEW_UI === 'true';

app.get('/', (req, res) => {
  res.json({
    message: `Project 08 — Multi-Environment Pipeline`,
    environment: ENV,
    version: VERSION,
    feature_new_ui: FEATURE_FLAG,
  });
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', environment: ENV });
});

app.get('/api/config', (req, res) => {
  res.json({
    environment: ENV,
    version: VERSION,
    features: { new_ui: FEATURE_FLAG },
    timestamp: new Date().toISOString(),
  });
});

app.use((_req, res) => res.status(404).json({ error: 'Not found' }));

if (require.main === module) {
  app.listen(PORT, () => console.log(`[${ENV}] App on :${PORT}`));
}

module.exports = app;
