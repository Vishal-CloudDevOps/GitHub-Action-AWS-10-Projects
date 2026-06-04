/**
 * Project 10 — Enterprise Pipeline Demo App
 * This app is the deployment target for the full enterprise
 * pipeline with versioning, SBOM, notifications, and rollback.
 */

const express = require('express');
const os = require('os');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

const BUILD_INFO = {
  version: process.env.APP_VERSION || '0.0.0',
  commit: process.env.GIT_SHA || 'unknown',
  build_number: process.env.BUILD_NUMBER || '0',
  environment: process.env.NODE_ENV || 'development',
  built_at: process.env.BUILT_AT || new Date().toISOString(),
};

app.get('/', (req, res) => {
  res.json({
    name: 'project-10-enterprise-pipeline',
    ...BUILD_INFO,
    hostname: os.hostname(),
  });
});

app.get('/health', (req, res) => res.status(200).json({ status: 'healthy' }));
app.get('/version', (req, res) => res.json(BUILD_INFO));
app.get('/ready', (req, res) => res.status(200).json({ status: 'ready' }));
app.use((_req, res) => res.status(404).json({ error: 'Not found' }));

if (require.main === module) {
  process.on('SIGTERM', () => { console.log('SIGTERM — shutting down'); process.exit(0); });
  app.listen(PORT, () => console.log(`Enterprise app v${BUILD_INFO.version} on :${PORT}`));
}

module.exports = app;
