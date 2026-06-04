import React, { useState, useEffect } from 'react';

function App() {
  const [count, setCount] = useState(0);
  const [deployInfo, setDeployInfo] = useState({});

  useEffect(() => {
    setDeployInfo({
      version: process.env.REACT_APP_VERSION || 'local',
      environment: process.env.REACT_APP_ENV || 'development',
      builtAt: process.env.REACT_APP_BUILD_DATE || new Date().toISOString(),
    });
  }, []);

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 600, margin: '4rem auto', textAlign: 'center' }}>
      <h1>🚀 Project 04 — React + S3 + CloudFront</h1>
      <p>Deployed via GitHub Actions to AWS S3 with CloudFront CDN</p>
      <button
        onClick={() => setCount(c => c + 1)}
        style={{ padding: '0.75rem 1.5rem', fontSize: '1rem', borderRadius: 6, cursor: 'pointer' }}
      >
        Clicked {count} {count === 1 ? 'time' : 'times'}
      </button>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f0f0f0', borderRadius: 8 }}>
        <h3>📦 Deployment Info</h3>
        <p><strong>Version:</strong> {deployInfo.version}</p>
        <p><strong>Environment:</strong> {deployInfo.environment}</p>
        <p><strong>Built at:</strong> {deployInfo.builtAt}</p>
      </div>
    </div>
  );
}

export default App;
