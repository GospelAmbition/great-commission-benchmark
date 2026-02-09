import { ApiClient } from '@/lib/api';

// Mock fetch
global.fetch = jest.fn();

describe('ApiClient', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = new ApiClient('http://localhost:8001');
    (fetch as jest.Mock).mockClear();
  });

  describe('getLeaderboard', () => {
    it('makes GET request to leaderboard endpoint', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      });

      await apiClient.getLeaderboard({ limit: 10 });

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/public/leaderboard?limit=10',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('handles multiple query parameters', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      });

      await apiClient.getLeaderboard({
        version: '1.0',
        category: 'scripture',
        limit: 20,
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('version=1.0'),
        expect.any(Object)
      );
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('category=scripture'),
        expect.any(Object)
      );
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=20'),
        expect.any(Object)
      );
    });
  });

  describe('getModels', () => {
    it('makes GET request to models endpoint', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [] }),
      });

      await apiClient.getModels();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/public/models',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });
  });

  describe('compareModels', () => {
    it('makes POST request with model IDs', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ models: [] }),
      });

      await apiClient.compareModels(['model1', 'model2']);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/public/leaderboard/compare?models=model1&models=model2',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });
  });

  describe('error handling', () => {
    it('throws error on non-ok response', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ detail: 'Not found' }),
      });

      await expect(apiClient.getModels()).rejects.toThrow('Not found');
    });
  });
});
