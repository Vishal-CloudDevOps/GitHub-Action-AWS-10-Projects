const express = require('express');
const os = require('os');
const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({
    message: 'Project 03 — Dockerized App',
    container_id: os.hostname(),
    version: process.env.APP_VERSION || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
  });
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', pid: process.pid, uptime: process.uptime() });
});

app.get('/api/info', (req, res) => {
  res.json({
    node: process.version,
    platform: os.platform(),
    arch: os.arch(),
    memory_mb: Math.round(os.freemem() / 1024 / 1024),
  });
});

app.use((_req, res) => res.status(404).json({ error: 'Not found' }));

if (require.main === module) {
  app.listen(PORT, '0.0.0.0', () => console.log(`🐳 Docker app on port ${PORT}`));
}

module.exports = app;
