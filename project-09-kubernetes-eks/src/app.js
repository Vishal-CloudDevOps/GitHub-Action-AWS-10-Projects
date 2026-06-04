const express = require('express');
const os = require('os');
const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({
    message: 'Project 09 — Kubernetes EKS Deployment',
    version: process.env.APP_VERSION || '1.0.0',
    pod_name: os.hostname(),
    namespace: process.env.K8S_NAMESPACE || 'default',
    node_name: process.env.K8S_NODE_NAME || 'unknown',
  });
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', uptime: process.uptime() });
});

app.get('/ready', (req, res) => {
  // Readiness probe — confirms the app is ready to receive traffic
  res.status(200).json({ status: 'ready' });
});

app.get('/api/pods', (req, res) => {
  res.json({
    current_pod: os.hostname(),
    namespace: process.env.K8S_NAMESPACE || 'default',
    replica_hint: 'Hit this endpoint multiple times to see different pods',
  });
});

app.use((_req, res) => res.status(404).json({ error: 'Not found' }));

if (require.main === module) {
  // Graceful shutdown on SIGTERM (Kubernetes sends this before killing pod)
  process.on('SIGTERM', () => {
    console.log('SIGTERM received — shutting down gracefully');
    process.exit(0);
  });
  app.listen(PORT, '0.0.0.0', () => console.log(`K8s app on :${PORT}`));
}

module.exports = app;
