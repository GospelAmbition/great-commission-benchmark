/**
 * API client for Great Commission Benchmark backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiError {
  detail: string;
}

// Response types
export interface LeaderboardItem {
  model_id: string;
  model_name: string;
  provider: string;
  overall_score: number;
  tier1_score?: number;
  tier2_score?: number;
  tier3_score?: number;
  trust_tier?: string;
  test_count?: number;
  category_scores?: Record<string, number>;
}

export interface LeaderboardResponse {
  items: LeaderboardItem[];
  total: number;
}

// Backend response types (different structure from frontend)
interface BackendLeaderboardEntry {
  model?: { id?: string; model_id?: string; name?: string; provider?: string };
  scores?: { overall?: number; tier1?: number; tier2?: number; tier3?: number };
  test_run?: { trust_tier?: string };
  category_scores?: Record<string, number>;
}

interface BackendLeaderboardResponse {
  entries: BackendLeaderboardEntry[];
  total_models: number;
}

export interface ModelResponse {
  id: string;
  model_id: string;
  model_name?: string;
  name?: string;
  provider: string;
  overall_score?: number;
  score?: number;
  tier1_score?: number;
  tier2_score?: number;
  tier3_score?: number;
  trust_tier?: string;
  test_count?: number;
  category_scores?: Record<string, number>;
  version_history?: Array<{ version: string; score: number; date: string }>;
}

export interface ModelsResponse {
  items: ModelResponse[];
  total: number;
}

export interface VersionResponse {
  version: string;
  is_current: boolean;
  question_count: number;
  tier1_count?: number;
  tier2_count?: number;
  tier3_count?: number;
}

export interface VersionsResponse {
  versions: VersionResponse[];
}

export interface StatsResponse {
  total_models: number;
  average_score?: number;
  last_updated: string;
}

export interface CompareResponse {
  models: Array<{
    model_id: string;
    model_name: string;
    provider: string;
    overall_score: number;
    tier1_score?: number;
    tier2_score?: number;
    tier3_score?: number;
    category_scores?: Record<string, number>;
  }>;
  categories: string[];
  category_breakdown?: Record<string, number[]>;
}

export interface UserProfile {
  id: string;
  name?: string;
  email: string;
  organization?: string;
  test_count?: number;
  contribution_count?: number;
}

export interface TestRun {
  id: string;
  model_id: string;
  model_name?: string;
  version: string;
  status: string;
  overall_score?: number;
  tier1_score?: number;
  tier2_score?: number;
  tier3_score?: number;
  category_scores?: Record<string, number>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  total_questions?: number;
  completed_questions?: number;
  system_prompt?: string;
  estimated_cost?: number;
}

export interface TestsResponse {
  items: TestRun[];
  total: number;
}

export interface TestProgress {
  status: string;
  completed_questions: number;
  total_questions: number;
  current_tier?: string;
  current_category?: string;
  estimated_time_remaining_minutes?: number;
}

export interface TestResult {
  id: string;
  question_id: string;
  question_content?: string;
  question_category?: string;
  question_tier?: string;
  response?: string;
  verdict: string;
  reasoning?: string;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = await this.getAuthToken();

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  private async getAuthToken(): Promise<string | null> {
    // In a real implementation, get token from Auth0 session
    // For now, return null (public endpoints)
    return null;
  }

  // Public API endpoints
  async getLeaderboard(params?: {
    version?: string;
    category?: string;
    tier?: string;
    provider?: string;
    trust_tier?: string;
    limit?: number;
    offset?: number;
    sort?: string;
    order?: 'asc' | 'desc';
  }): Promise<LeaderboardResponse> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        // Skip undefined and empty strings to avoid backend validation errors
        if (value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    const response = await this.request<BackendLeaderboardResponse>(`/api/public/leaderboard${query ? `?${query}` : ''}`);
    
    // Transform backend response to frontend format
    return {
      items: (response.entries || []).map((entry) => ({
        model_id: entry.model?.model_id || entry.model?.id || '',
        model_name: entry.model?.name || '',
        provider: entry.model?.provider || '',
        overall_score: entry.scores?.overall || 0,
        tier1_score: entry.scores?.tier1,
        tier2_score: entry.scores?.tier2,
        tier3_score: entry.scores?.tier3,
        trust_tier: entry.test_run?.trust_tier,
        test_count: 1, // Single test run per entry
        category_scores: entry.category_scores || {},
      })),
      total: response.total_models || 0,
    };
  }

  async getModels(params?: { limit?: number; offset?: number }): Promise<ModelsResponse> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        // Skip undefined values to avoid backend validation errors
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<ModelsResponse>(`/api/public/models${query ? `?${query}` : ''}`);
  }

  async getModel(id: string): Promise<ModelResponse> {
    return this.request<ModelResponse>(`/api/public/models/${id}`);
  }

  async getVersions(): Promise<VersionsResponse> {
    return this.request<VersionsResponse>('/api/public/versions');
  }

  async getStats(): Promise<StatsResponse> {
    return this.request<StatsResponse>('/api/public/stats');
  }

  async compareModels(modelIds: string[]): Promise<CompareResponse> {
    return this.request<CompareResponse>('/api/public/leaderboard/compare', {
      method: 'POST',
      body: JSON.stringify({ model_ids: modelIds }),
    });
  }

  // User API endpoints (require auth)
  async getUserProfile(): Promise<UserProfile> {
    return this.request<UserProfile>('/api/user/profile');
  }

  async updateUserProfile(data: { name?: string; organization?: string }): Promise<UserProfile> {
    return this.request<UserProfile>('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getUserTests(params?: {
    status?: string;
    model_id?: string;
    version?: string;
    limit?: number;
    offset?: number;
  }): Promise<TestsResponse> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        // Skip undefined and empty strings to avoid backend validation errors
        if (value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<TestsResponse>(`/api/user/tests${query ? `?${query}` : ''}`);
  }

  async getTest(id: string): Promise<TestRun> {
    return this.request<TestRun>(`/api/user/tests/${id}`);
  }

  async getTestResults(id: string): Promise<TestResult[]> {
    return this.request<TestResult[]>(`/api/user/tests/${id}/results`);
  }

  // Tests API
  async createTest(data: {
    model_id: string;
    version: string;
    system_prompt?: string;
  }): Promise<TestRun> {
    return this.request<TestRun>('/api/tests', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async startTest(id: string): Promise<TestRun> {
    return this.request<TestRun>(`/api/tests/${id}/start`, {
      method: 'POST',
    });
  }

  async getTestProgress(id: string): Promise<TestProgress> {
    return this.request<TestProgress>(`/api/tests/${id}/progress`);
  }

  async cancelTest(id: string): Promise<TestRun> {
    return this.request<TestRun>(`/api/tests/${id}/cancel`, {
      method: 'POST',
    });
  }

  // Newsletter
  async subscribeNewsletter(email: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/newsletter/subscribe', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  // User submissions and activity
  async getUserSubmissions(): Promise<Array<{
    id: string;
    model_name: string;
    status: string;
    created_at: string;
  }>> {
    return this.request('/api/user/submissions');
  }

  async getUserActivity(params?: { limit?: number }): Promise<Array<{
    type: string;
    description?: string;
    created_at: string;
    link?: string;
  }>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        // Skip undefined values to avoid backend validation errors
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request(`/api/user/activity${query ? `?${query}` : ''}`);
  }

  // Tester Agreement
  async acceptTesterAgreement(): Promise<{ message: string; accepted: boolean }> {
    return this.request('/api/user/tester-agreement/accept', {
      method: 'POST',
    });
  }

  async getProfile(): Promise<UserProfile & { tester_agreement_accepted?: boolean }> {
    return this.request('/api/user/profile');
  }

  // Payments API
  async createPaymentIntent(testId: string, tipPercentage?: number): Promise<{
    payment_intent_id: string;
    client_secret: string;
    amount: number;
    breakdown: {
      api_cost: number;
      processing_fee: number;
      tip_amount: number;
      total: number;
    };
  }> {
    return this.request(`/api/v1/payments/create-intent`, {
      method: 'POST',
      body: JSON.stringify({
        test_id: testId,
        tip_percentage: tipPercentage,
      }),
    });
  }

  async createRefund(testId: string, amount?: number): Promise<{
    refund_id: string;
    amount: number;
    status: string;
  }> {
    return this.request(`/api/v1/payments/refund`, {
      method: 'POST',
      body: JSON.stringify({
        test_id: testId,
        amount: amount,
      }),
    });
  }
}

export const apiClient = new ApiClient();
