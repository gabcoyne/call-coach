import { NextRequest } from 'next/server';
import { POST, GET } from '../route';
import { exec } from 'child_process';

// Mock child_process
jest.mock('child_process');
const mockExec = exec as jest.MockedFunction<typeof exec>;

describe('GET /api/cron/daily-sync', () => {
  it('should return cron job configuration', async () => {
    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'GET',
    });

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toMatchObject({
      job: 'daily-gong-sync',
      schedule: '0 6 * * *',
      description: expect.any(String),
    });
  });
});

describe('POST /api/cron/daily-sync', () => {
  const mockCronSecret = 'test-cron-secret-123';

  beforeEach(() => {
    jest.clearAllMocks();
    process.env.CRON_SECRET = mockCronSecret;
  });

  afterEach(() => {
    delete process.env.CRON_SECRET;
  });

  it('should reject unauthorized requests', async () => {
    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer wrong-secret',
      },
    });

    const response = await POST(request);

    expect(response.status).toBe(401);
    const data = await response.json();
    expect(data).toEqual({ error: 'Unauthorized' });
  });

  it('should reject requests without authorization header', async () => {
    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'POST',
    });

    const response = await POST(request);

    expect(response.status).toBe(401);
  });

  it('should execute sync successfully with valid authorization', async () => {
    // Mock successful execution
    const mockStdout = JSON.stringify({
      status: 'success',
      opportunities: { synced: 10, errors: 0 },
      associations: { calls_linked: 25, emails_synced: 15 },
    });

    mockExec.mockImplementation((command: any, options: any, callback: any) => {
      callback(null, { stdout: mockStdout, stderr: '' });
      return {} as any;
    });

    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${mockCronSecret}`,
      },
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toMatchObject({
      job: 'daily-gong-sync',
      status: 'success',
      output: expect.any(String),
    });
    expect(data.startTime).toBeTruthy();
    expect(data.endTime).toBeTruthy();
  });

  it('should handle sync failures gracefully', async () => {
    // Mock failed execution
    const mockError = new Error('Python script failed') as any;
    mockError.stdout = 'Partial output';
    mockError.stderr = 'Error details';

    mockExec.mockImplementation((command: any, options: any, callback: any) => {
      callback(mockError);
      return {} as any;
    });

    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${mockCronSecret}`,
      },
    });

    const response = await POST(request);

    // Should return 200 even on sync failure (job executed, sync failed)
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toMatchObject({
      job: 'daily-gong-sync',
      status: 'failed',
      error: expect.any(String),
    });
  });

  it('should allow requests in development without CRON_SECRET', async () => {
    delete process.env.CRON_SECRET;

    mockExec.mockImplementation((command: any, options: any, callback: any) => {
      callback(null, { stdout: 'Success', stderr: '' });
      return {} as any;
    });

    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'POST',
    });

    const response = await POST(request);

    // Should allow in development (no CRON_SECRET configured)
    expect(response.status).toBe(200);
  });

  it('should execute with correct Python command', async () => {
    mockExec.mockImplementation((command: any, options: any, callback: any) => {
      callback(null, { stdout: 'Success', stderr: '' });
      return {} as any;
    });

    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${mockCronSecret}`,
      },
    });

    await POST(request);

    expect(mockExec).toHaveBeenCalledWith(
      expect.stringContaining('uv run python -m flows.daily_gong_sync'),
      expect.objectContaining({
        timeout: 280000, // 280s timeout
        maxBuffer: 10 * 1024 * 1024, // 10MB
      }),
      expect.any(Function)
    );
  });

  it('should handle timeout errors', async () => {
    const timeoutError = new Error('Execution timed out') as any;
    timeoutError.code = 'ETIMEDOUT';

    mockExec.mockImplementation((command: any, options: any, callback: any) => {
      callback(timeoutError);
      return {} as any;
    });

    const request = new NextRequest('http://localhost/api/cron/daily-sync', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${mockCronSecret}`,
      },
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.status).toBe('failed');
    expect(data.error).toContain('timed out');
  });
});
