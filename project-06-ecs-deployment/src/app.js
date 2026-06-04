const express = require('express');
const os = require('os');
const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({
    message: 'Project 06 — ECS Fargate Deployment',
    version: process.env.APP_VERSION || '1.0.0',
    container_id: os.hostname(),
    environment: process.env.NODE_ENV || 'production',
  });
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', uptime: process.uptime() });
});

app.get('/api/info', (req, res) => {
  res.json({
    node: process.version,
    platform: os.platform(),
    memory_mb: Math.round(process.memoryUsage().rss / 1024 / 1024),
  });
});

app.use((_req, res) => res.status(404).json({ error: 'Not found' }));

if (require.main === module) {
  app.listen(PORT, '0.0.0.0', () => console.log(`ECS app on :${PORT}`));
}

module.exports = app;
