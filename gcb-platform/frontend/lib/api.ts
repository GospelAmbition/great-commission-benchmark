/**
 * API client for Great Commission Benchmark backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiError {
  detail: string;
}

// Response types
export interface LeaderboardItem {
  id: string; // UUID for API operations (e.g., compare)
  model_id: string; // OpenRouter-style ID (e.g., "openai/gpt-4")
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
  test_history?: Array<{
    test_run_id: string;
    overall_score: number;
    benchmark_version: string;
    completed_at: string;
    trust_tier: string;
  }>;
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
  role?: 'user' | 'moderator' | 'blog_manager' | 'benchmark_developer' | 'admin';
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

  /**
   * Build a query string from an object of params, filtering out undefined/empty values.
   * @param params - Object with key-value pairs for query params
   * @param options - Optional config (skipEmpty to also skip empty strings)
   */
  private buildQueryString(
    params?: Record<string, string | number | boolean | undefined>,
    options: { skipEmpty?: boolean } = {}
  ): string {
    if (!params) return '';
    
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined) return;
      if (options.skipEmpty && value === '') return;
      queryParams.append(key, String(value));
    });
    
    const query = queryParams.toString();
    return query ? `?${query}` : '';
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
    // Transform tier string (e.g., "tier1") to integer (e.g., "1") for backend
    const transformedParams = params ? {
      ...params,
      tier: params.tier?.startsWith('tier') ? params.tier.replace('tier', '') : params.tier,
    } : undefined;
    
    const query = this.buildQueryString(transformedParams, { skipEmpty: true });
    const response = await this.request<BackendLeaderboardResponse>(`/api/public/leaderboard${query}`);
    
    // Transform backend response to frontend format
    return {
      items: (response.entries || []).map((entry) => ({
        id: entry.model?.id || '', // UUID for API operations
        model_id: entry.model?.model_id || entry.model?.id || '', // OpenRouter-style ID for display/routing
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
    return this.request<ModelsResponse>(`/api/public/models${this.buildQueryString(params)}`);
  }

  async getAvailableModels(params?: { search?: string; limit?: number }): Promise<ModelsResponse> {
    return this.request<ModelsResponse>(`/api/public/available-models${this.buildQueryString(params)}`);
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
    const params = modelIds.map(id => `models=${encodeURIComponent(id)}`).join('&');
    
    // Backend returns nested structure, transform to flat structure for frontend
    interface BackendCompareResponse {
      semantic_version: string;
      marketing_version: string;
      models: Array<{
        model: { id: string; name: string; provider: string };
        test_run_id: string;
        scores: { overall: number; tier1: number; tier2: number; tier3: number; category_scores?: Record<string, number> };
        verdict_distribution: Record<string, number>;
      }>;
      comparison: { score_delta?: { overall: number; tier1: number; tier2: number; tier3: number } };
    }
    
    const response = await this.request<BackendCompareResponse>(`/api/public/leaderboard/compare?${params}`);
    
    // Transform to frontend format
    const allCategories = new Set<string>();
    const transformedModels = (response.models || []).map((entry) => {
      const categoryScores = entry.scores?.category_scores || {};
      Object.keys(categoryScores).forEach(cat => allCategories.add(cat));
      
      return {
        model_id: entry.model?.id || '',
        model_name: entry.model?.name || '',
        provider: entry.model?.provider || '',
        overall_score: entry.scores?.overall || 0,
        tier1_score: entry.scores?.tier1,
        tier2_score: entry.scores?.tier2,
        tier3_score: entry.scores?.tier3,
        category_scores: categoryScores,
      };
    });
    
    return {
      models: transformedModels,
      categories: Array.from(allCategories),
      category_breakdown: undefined,
    };
  }

  // User API endpoints (require auth)
  async getUserProfile(): Promise<UserProfile & { test_count?: number; contribution_count?: number; tester_agreement_accepted?: boolean }> {
    // Backend returns { user: {...}, stats: {...} }, transform to flat structure
    const response = await this.request<{ user: UserProfile & { tester_agreement_accepted?: boolean }; stats: { total_tests: number; total_submissions: number; total_contribution: number } }>('/api/user/profile');
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
    // Backend returns { tests: [...], pagination: {...} }, transform to { items: [...], total: ... }
    const response = await this.request<{ tests: any[]; pagination: { total: number } }>(
      `/api/user/tests${this.buildQueryString(params, { skipEmpty: true })}`
    );
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
    overall_score?: number;
  }>> {
    // Backend returns { submissions: [...], pagination: {...} }, extract the array
    const response = await this.request<{ submissions: Array<{ id: string; model_name: string; status: string; submitted_at: string; overall_score?: number }> }>('/api/user/submissions');
    return (response.submissions || []).map((sub) => ({
      id: sub.id,
      model_name: sub.model_name,
      status: sub.status,
      created_at: sub.submitted_at, // Map submitted_at to created_at for frontend compatibility
      overall_score: sub.overall_score,
    }));
  }

  async getUserSubmissionDetail(submissionId: string): Promise<{
    id: string;
    model_name: string;
    status: string;
    cli_version: string;
    question_set_version: string;
    overall_score: number;
    tier1_score: number;
    tier2_score: number;
    tier3_score: number;
    total_questions: number;
    verdict_counts: Record<string, number>;
    submitted_at: string | null;
    reviewed_at: string | null;
    reviewer_notes: string | null;
    judge_model: string | null;
    backend: string | null;
    completed_at: string | null;
    responses: Array<{
      question_id: string;
      tier: number;
      category: string;
      response: string;
      verdict: string;
      verdict_normalized?: string;
      judge_reasoning?: string;
      response_time_ms?: number;
    }>;
    fee_waived: boolean;
  }> {
    return this.request(`/api/user/submissions/${submissionId}`);
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
    // Backend returns { activities: [...] }, extract the array
    const response = await this.request<{ activities: Array<{ type: string; title: string; description: string; timestamp: string; link?: string }> }>(
      `/api/user/activity${this.buildQueryString(params)}`
    );
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

  // Donations API (no auth required)
  async createDonationIntent(amount: number, email?: string): Promise<{
    payment_intent_id: string;
    client_secret: string;
    amount: number;
  }> {
    return this.request(`/api/v1/donations/create-intent`, {
      method: 'POST',
      body: JSON.stringify({
        amount,
        email: email || undefined,
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
    return this.request(`/api/moderator/queue${this.buildQueryString(params)}`);
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
    return this.request(`/api/moderator/community${this.buildQueryString(params)}`);
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
    return this.request(`/api/moderator/activity${this.buildQueryString(params)}`);
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
    return this.request(`/api/user/sponsorship${this.buildQueryString(params)}`);
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
    return this.request(`/api/moderator/sponsorship${this.buildQueryString(params)}`);
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

  // =============================================================================
  // Blog API endpoints
  // =============================================================================

  // Public blog endpoints
  async getBlogPosts(params?: {
    category?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    items: BlogPost[];
    total: number;
  }> {
    return this.request(`/api/blog/posts${this.buildQueryString(params)}`);
  }

  async getBlogPost(slug: string): Promise<BlogPost> {
    return this.request(`/api/blog/posts/${slug}`);
  }

  async getBlogCategories(): Promise<{
    items: BlogCategory[];
    total: number;
  }> {
    return this.request('/api/blog/categories');
  }

  // Admin blog endpoints
  async getAdminBlogPosts(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    items: BlogPost[];
    total: number;
  }> {
    return this.request(`/api/admin/blog/posts${this.buildQueryString(params)}`);
  }

  async getAdminBlogPost(id: string): Promise<BlogPost> {
    return this.request(`/api/admin/blog/posts/${id}`);
  }

  async createBlogPost(data: {
    title: string;
    slug: string;
    excerpt?: string;
    content?: string;
    featured_image_url?: string;
    category_ids?: string[];
  }): Promise<BlogPost> {
    return this.request('/api/admin/blog/posts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateBlogPost(id: string, data: {
    title?: string;
    slug?: string;
    excerpt?: string;
    content?: string;
    featured_image_url?: string;
    category_ids?: string[];
  }): Promise<BlogPost> {
    return this.request(`/api/admin/blog/posts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteBlogPost(id: string): Promise<{ message: string }> {
    return this.request(`/api/admin/blog/posts/${id}`, {
      method: 'DELETE',
    });
  }

  async publishBlogPost(id: string): Promise<BlogPost> {
    return this.request(`/api/admin/blog/posts/${id}/publish`, {
      method: 'POST',
    });
  }

  async unpublishBlogPost(id: string): Promise<BlogPost> {
    return this.request(`/api/admin/blog/posts/${id}/unpublish`, {
      method: 'POST',
    });
  }

  async uploadBlogImage(file: File): Promise<{
    url: string;
    filename: string;
    size: number;
    content_type: string;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = await this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/api/admin/blog/upload-image`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload image');
    }

    return response.json();
  }

  // Admin blog category endpoints
  async getAdminBlogCategories(): Promise<{
    items: BlogCategory[];
    total: number;
  }> {
    return this.request('/api/admin/blog/categories');
  }

  async createBlogCategory(data: {
    name: string;
    slug: string;
    description?: string;
  }): Promise<BlogCategory> {
    return this.request('/api/admin/blog/categories', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateBlogCategory(id: string, data: {
    name?: string;
    slug?: string;
    description?: string;
  }): Promise<BlogCategory> {
    return this.request(`/api/admin/blog/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteBlogCategory(id: string): Promise<{ message: string }> {
    return this.request(`/api/admin/blog/categories/${id}`, {
      method: 'DELETE',
    });
  }
}

// Blog types
export interface BlogCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt?: string;
  content?: string;
  featured_image_url?: string;
  status: string;
  author: {
    id: string;
    name?: string;
    email: string;
  };
  categories: BlogCategory[];
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export const apiClient = new ApiClient();
