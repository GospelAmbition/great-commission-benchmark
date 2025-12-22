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
  total_models_tested: number;
  total_test_runs: number;
  current_benchmark_version: string;
  top_score: number;
  average_score: number;
  providers_represented: number;
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
  role?: 'user' | 'moderator' | 'benchmark_developer' | 'admin';
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
  
  // Token caching to avoid redundant /api/auth/token requests
  private cachedToken: string | null = null;
  private tokenExpiresAt: number = 0;
  private pendingTokenRequest: Promise<string | null> | null = null;
  
  // Cache token for 55 minutes (token is valid for 1 hour)
  private static TOKEN_CACHE_DURATION_MS = 55 * 60 * 1000;

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
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorDetail = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        } else if (errorData.message) {
          errorDetail = errorData.message;
        } else {
          errorDetail = JSON.stringify(errorData);
        }
      } catch {
        // If JSON parsing fails, use the default error message
      }
      throw new Error(errorDetail);
    }

    return response.json();
  }

  private async getAuthToken(): Promise<string | null> {
    // Return cached token if still valid
    if (this.cachedToken && Date.now() < this.tokenExpiresAt) {
      return this.cachedToken;
    }
    
    // If there's already a pending request, wait for it instead of making a new one
    if (this.pendingTokenRequest) {
      return this.pendingTokenRequest;
    }
    
    // Fetch new token
    this.pendingTokenRequest = this.fetchAuthToken();
    
    try {
      const token = await this.pendingTokenRequest;
      return token;
    } finally {
      this.pendingTokenRequest = null;
    }
  }
  
  private async fetchAuthToken(): Promise<string | null> {
    try {
      const response = await fetch('/api/auth/token');
      if (response.ok) {
        const data = await response.json();
        const token = data.token || null;
        
        if (token) {
          this.cachedToken = token;
          this.tokenExpiresAt = Date.now() + ApiClient.TOKEN_CACHE_DURATION_MS;
        }
        
        return token;
      }
    } catch (error) {
      // Silently fail - user may not be authenticated
      return null;
    }
    return null;
  }
  
  // Clear cached token (useful for logout)
  public clearTokenCache(): void {
    this.cachedToken = null;
    this.tokenExpiresAt = 0;
    this.pendingTokenRequest = null;
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
          // Convert tier string (e.g., "tier1") to integer (e.g., "1") for backend
          if (key === 'tier' && typeof value === 'string' && value.startsWith('tier')) {
            queryParams.append(key, value.replace('tier', ''));
          } else {
            queryParams.append(key, String(value));
          }
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

  async getAvailableModels(params?: { search?: string; limit?: number }): Promise<ModelsResponse> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<ModelsResponse>(`/api/public/available-models${query ? `?${query}` : ''}`);
  }

  async getModel(id: string): Promise<ModelResponse> {
    // Model IDs with slashes (e.g., "qwen/qwen3-coder-30b") need special handling
    // Use query parameter instead of path parameter to avoid URL encoding issues
    const params = new URLSearchParams({ model_id: id });
    return this.request<ModelResponse>(`/api/public/models/by-id?${params.toString()}`);
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
  async getUserProfile(): Promise<UserProfile & { test_count?: number; contribution_count?: number }> {
    // Backend returns { user: {...}, stats: {...} }, transform to flat structure
    const response = await this.request<{ user: UserProfile; stats: { total_tests: number; total_submissions: number; total_contribution: number } }>('/api/user/profile');
    return {
      ...response.user,
      test_count: response.stats?.total_tests || 0,
      contribution_count: response.stats?.total_submissions || 0,
    };
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
    // Backend returns { tests: [...], pagination: {...} }, transform to { items: [...], total: ... }
    const response = await this.request<{ tests: any[]; pagination: { total: number } }>(`/api/user/tests${query ? `?${query}` : ''}`);
    return {
      items: (response.tests || []).map((test) => ({
        id: test.id,
        model_id: test.model?.model_id || test.model?.id || '',
        model_name: test.model?.name || '',
        version: test.benchmark_version || '',
        status: test.status || 'pending',
        overall_score: test.scores?.overall,
        tier1_score: test.scores?.tier1,
        tier2_score: test.scores?.tier2,
        tier3_score: test.scores?.tier3,
        created_at: test.created_at,
        started_at: test.started_at,
        completed_at: test.completed_at,
        trust_tier: test.trust_tier,
      })),
      total: response.pagination?.total || 0,
    };
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
    // Backend returns { submissions: [...], pagination: {...} }, extract the array
    const response = await this.request<{ submissions: Array<{ id: string; model_name: string; status: string; submitted_at: string }> }>('/api/user/submissions');
    return (response.submissions || []).map((sub) => ({
      id: sub.id,
      model_name: sub.model_name,
      status: sub.status,
      created_at: sub.submitted_at, // Map submitted_at to created_at for frontend compatibility
    }));
  }

  async uploadCliSubmission(exportData: object): Promise<{
    submission_id: string;
    status: string;
    validation_errors?: string[] | null;
    message: string;
    fee_waived?: boolean;
    payment_required?: boolean;
    payment_intent_id?: string;
    payment_url?: string;
  }> {
    return this.request('/api/submissions', {
      method: 'POST',
      body: JSON.stringify({ export_data: exportData }),
    });
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
    // Backend returns { activities: [...] }, extract the array
    const response = await this.request<{ activities: Array<{ type: string; title: string; description: string; timestamp: string; link?: string }> }>(`/api/user/activity${query ? `?${query}` : ''}`);
    return (response.activities || []).map((activity) => ({
      type: activity.type,
      description: activity.description || activity.title,
      created_at: activity.timestamp,
      link: activity.link,
    }));
  }

  // Tester Agreement
  async acceptTesterAgreement(): Promise<{ message: string; accepted: boolean }> {
    return this.request('/api/user/tester-agreement/accept', {
      method: 'POST',
    });
  }

  async getProfile(): Promise<UserProfile & { tester_agreement_accepted?: boolean }> {
    // The API returns { user: {...}, stats: {...} }, extract the user
    const response = await this.request<{ user: UserProfile & { tester_agreement_accepted?: boolean }; stats: unknown }>('/api/user/profile');
    return response.user;
  }

  // API Keys
  async getAPIKeys(): Promise<{
    api_keys: Array<{
      id: string;
      name: string;
      key_prefix: string;
      is_active: boolean;
      last_used_at: string | null;
      created_at: string;
      expires_at: string | null;
    }>;
    total: number;
  }> {
    return this.request('/api/user/api-keys');
  }

  async createAPIKey(name: string): Promise<{
    id: string;
    name: string;
    key: string;
    key_prefix: string;
    created_at: string;
    message: string;
  }> {
    return this.request('/api/user/api-keys', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async revokeAPIKey(keyId: string): Promise<{
    id: string;
    message: string;
  }> {
    return this.request(`/api/user/api-keys/${keyId}`, {
      method: 'DELETE',
    });
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

  // Payment dev mode methods
  async checkPaymentDevMode(): Promise<{
    dev_mode: boolean;
    stripe_configured: boolean;
  }> {
    return this.request(`/api/v1/payments/dev-mode`);
  }

  async devCompletePayment(testId: string): Promise<{
    test_id: string;
    status: string;
    payment_status: string;
    total_cost: number;
    message: string;
  }> {
    return this.request(`/api/v1/payments/dev-complete`, {
      method: 'POST',
      body: JSON.stringify({
        test_id: testId,
        accepted_cost: true,
      }),
    });
  }

  // Moderator API endpoints
  async getModerationQueue(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    items: Array<{
      test_id: string;
      model_name: string;
      user_name: string;
      overall_score?: number;
      status: string;
      trust_tier: string;
      created_at: string;
      priority: number;
    }>;
    total: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request(`/api/moderator/queue${query ? `?${query}` : ''}`);
  }

  async getCommunitySubmissionQueue(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    items: Array<{
      submission_id: string;
      model_name: string;
      user_name: string;
      overall_score?: number;
      status: string;
      submitted_at: string;
    }>;
    total: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request(`/api/moderator/community${query ? `?${query}` : ''}`);
  }

  async getCommunitySubmissionDetail(submissionId: string): Promise<{
    submission_id: string;
    model_name: string;
    user_name: string;
    user_email: string;
    cli_version: string;
    question_set_version: string;
    overall_score: number;
    tier1_score: number;
    tier2_score: number;
    tier3_score: number;
    total_questions: number;
    status: string;
    submitted_at: string;
    results_package: any;
    sample_responses: Array<{
      question_id: string | number;
      tier: number;
      category: string;
      response: string;
      verdict: string;
      judge_reasoning?: string;
    }>;
    sample_size: number;
  }> {
    return this.request(`/api/moderator/community/${submissionId}`);
  }

  async reviewCommunitySubmission(submissionId: string, action: "approve" | "reject", notes?: string): Promise<{
    submission_id: string;
    status: string;
    message: string;
  }> {
    return this.request(`/api/moderator/community/${submissionId}/review`, {
      method: 'POST',
      body: JSON.stringify({ action, notes }),
    });
  }

  async getModeratorActivity(params?: {
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    items: Array<{
      review_id: string;
      test_id?: string | null;
      submission_id?: string | null;
      model_name: string;
      action: string;
      review_type: 'platform_test' | 'cli_submission';
      duration_seconds?: number | null;
      created_at: string;
    }>;
    total: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request(`/api/moderator/activity${query ? `?${query}` : ''}`);
  }

  async getModeratorStats(): Promise<{
    personal: {
      total_reviews: number;
      agreement_rate: number;
      agreements: number;
      disagreements: number;
    };
    system_wide: {
      total_reviews: number;
      pending_tests: number;
      agreement_rate: number;
      agreements: number;
      disagreements: number;
      completed_this_month?: number;
    };
  }> {
    return this.request('/api/moderator/stats');
  }

  async submitModerationReview(data: {
    test_id: string;
    verdict_reviews: Array<{
      result_id: string;
      verdict: 'agree' | 'disagree' | 'unsure';
      notes?: string;
    }>;
    overall_assessment: 'verified' | 'concerns' | 'escalated';
    notes?: string;
  }): Promise<{
    review_id: string;
    test_id: string;
    trust_tier: string;
    requires_second_review: boolean;
  }> {
    return this.request('/api/moderator/reviews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Sponsorship API endpoints
  async createSponsorship(data: {
    request_type: 'sponsorship' | 'request';
    openrouter_model_id?: string;
    custom_model_name?: string;
    message?: string;
  }): Promise<{
    id: string;
    request_type: string;
    model_name: string;
    status: string;
    payment_required: boolean;
    payment_intent_id?: string;
    client_secret?: string;
    message: string;
  }> {
    return this.request('/api/user/sponsorship', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getUserSponsorships(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{
    items: Array<{
      id: string;
      request_type: string;
      model_name: string;
      status: string;
      payment_status?: string;
      created_at: string;
      reviewed_at?: string;
      reviewer_notes?: string;
    }>;
    total: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request(`/api/user/sponsorship${query ? `?${query}` : ''}`);
  }

  async getSponsorshipQueue(params?: {
    status?: string;
    request_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    items: Array<{
      id: string;
      request_type: string;
      model_name: string;
      user_name: string;
      user_email: string;
      message?: string;
      status: string;
      payment_status?: string;
      created_at: string;
    }>;
    total: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request(`/api/moderator/sponsorship${query ? `?${query}` : ''}`);
  }

  async getSponsorshipDetail(id: string): Promise<{
    id: string;
    request_type: string;
    openrouter_model_id?: string;
    custom_model_name?: string;
    model_name: string;
    user_id: string;
    user_name: string;
    user_email: string;
    message?: string;
    status: string;
    payment_id?: string;
    payment_status?: string;
    created_at: string;
    reviewed_at?: string;
    reviewer_notes?: string;
  }> {
    return this.request(`/api/moderator/sponsorship/${id}`);
  }

  async reviewSponsorship(id: string, action: 'approve' | 'reject', notes?: string): Promise<{
    id: string;
    status: string;
    message: string;
  }> {
    return this.request(`/api/moderator/sponsorship/${id}/review`, {
      method: 'POST',
      body: JSON.stringify({ action, notes }),
    });
  }
}

export const apiClient = new ApiClient();
