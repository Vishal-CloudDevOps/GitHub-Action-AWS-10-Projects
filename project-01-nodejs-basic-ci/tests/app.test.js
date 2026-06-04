const request = require('supertest');
const app = require('../src/app');

// ─────────────────────────────────────────────────
// GET /
// ─────────────────────────────────────────────────
describe('GET /', () => {
  it('✅ returns 200 with welcome message', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.message).toContain('Hello');
  });

  it('❌ returns 404 for unknown route', async () => {
    const res = await request(app).get('/unknown');
    expect(res.statusCode).toBe(404);
    expect(res.body.error).toBe('Route not found');
  });
});

// ─────────────────────────────────────────────────
// GET /health
// ─────────────────────────────────────────────────
describe('GET /health', () => {
  it('✅ returns healthy with numeric uptime', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('healthy');
    expect(typeof res.body.uptime).toBe('number');
  });

  it('❌ POST /health returns 404', async () => {
    const res = await request(app).post('/health');
    expect(res.statusCode).toBe(404);
  });
});

// ─────────────────────────────────────────────────
// POST /api/add
// ─────────────────────────────────────────────────
describe('POST /api/add', () => {
  // Positive tests
  it('✅ adds two positive integers', async () => {
    const res = await request(app).post('/api/add').send({ a: 5, b: 3 });
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(8);
  });

  it('✅ adds negative numbers', async () => {
    const res = await request(app).post('/api/add').send({ a: -3, b: -7 });
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(-10);
  });

  it('✅ adds floats', async () => {
    const res = await request(app).post('/api/add').send({ a: 1.1, b: 2.2 });
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBeCloseTo(3.3);
  });

  it('✅ adds zero values', async () => {
    const res = await request(app).post('/api/add').send({ a: 0, b: 0 });
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(0);
  });

  // Negative tests
  it('❌ returns 400 when a is a string', async () => {
    const res = await request(app).post('/api/add').send({ a: 'foo', b: 3 });
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/numbers/i);
  });

  it('❌ returns 400 when b is missing', async () => {
    const res = await request(app).post('/api/add').send({ a: 5 });
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/required/i);
  });

  it('❌ returns 400 when body is empty', async () => {
    const res = await request(app).post('/api/add').send({});
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toBeDefined();
  });

  it('❌ returns 400 when both are null', async () => {
    const res = await request(app).post('/api/add').send({ a: null, b: null });
    expect(res.statusCode).toBe(400);
  });
});

// ─────────────────────────────────────────────────
// POST /api/multiply
// ─────────────────────────────────────────────────
describe('POST /api/multiply', () => {
  it('✅ multiplies two positive integers', async () => {
    const res = await request(app).post('/api/multiply').send({ a: 4, b: 5 });
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(20);
  });

  it('✅ multiplies by zero', async () => {
    const res = await request(app).post('/api/multiply').send({ a: 99, b: 0 });
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(0);
  });

  it('✅ multiplies negative numbers', async () => {
    const res = await request(app).post('/api/multiply').send({ a: -3, b: 4 });
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(-12);
  });

  it('❌ returns 400 when a is missing', async () => {
    const res = await request(app).post('/api/multiply').send({ b: 5 });
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/required/i);
  });

  it('❌ returns 400 when b is a boolean', async () => {
    const res = await request(app).post('/api/multiply').send({ a: 5, b: true });
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/numbers/i);
  });

  it('❌ returns 400 for array inputs', async () => {
    const res = await request(app).post('/api/multiply').send({ a: [1, 2], b: 3 });
    expect(res.statusCode).toBe(400);
  });
});
