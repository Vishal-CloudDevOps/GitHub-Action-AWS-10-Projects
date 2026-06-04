const request = require('supertest');
const app = require('../src/app');

describe('GET /', () => {
  it('returns app info', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toContain('Multi-Environment');
    expect(res.body.environment).toBeDefined();
  });
});

describe('GET /health', () => {
  it('returns healthy', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('healthy');
  });
});

describe('GET /api/config', () => {
  it('returns config object', async () => {
    const res = await request(app).get('/api/config');
    expect(res.statusCode).toBe(200);
    expect(res.body.environment).toBeDefined();
    expect(res.body.features).toBeDefined();
    expect(typeof res.body.features.new_ui).toBe('boolean');
  });
});

describe('Unknown route', () => {
  it('returns 404', async () => {
    const res = await request(app).get('/unknown');
    expect(res.statusCode).toBe(404);
  });
});
