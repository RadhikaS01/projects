const request = require('supertest');
const app = require('../src/index'); // Adjust the path as necessary

describe('Health Controller', () => {
    it('should return a 200 status and a health message', async () => {
        const response = await request(app).get('/health');
        expect(response.status).toBe(200);
        expect(response.body).toEqual({ message: 'Service is healthy' });
    });
});