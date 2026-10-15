import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import AdminDashboardPage from '@/app/admin/page';
import { toast } from 'sonner';

const mockRouter = { push: jest.fn() };
const mockSession = { data: { user: { id: 'admin' } }, status: 'authenticated' };
jest.mock('next/navigation', () => ({ useRouter: () => mockRouter }));
jest.mock('next-auth/react', () => ({ useSession: () => mockSession }));
jest.mock('@/lib/useUserProfile', () => ({
  useUserProfile: () => ({ canAdmin: true, isAdmin: true, loading: false }),
}));
jest.mock('sonner', () => ({ toast: { success: jest.fn(), error: jest.fn(), warning: jest.fn() } }));
const mockFetch = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = mockFetch;
});

function respond(body: unknown, ok = true) {
  return { ok, json: async () => body };
}

it('processes bounded batches to completion and totals the updates', async () => {
  mockFetch.mockResolvedValueOnce(respond({})); // Dashboard statistics
  mockFetch.mockResolvedValueOnce(respond({ updated_count: 2, total_models: 4, next_offset: 3 }));
  mockFetch.mockResolvedValueOnce(respond({ updated_count: 1, total_models: 4, next_offset: null, remaining_incomplete: 0, incomplete_model_ids: [] }));
  render(<AdminDashboardPage />);
  fireEvent.click(await screen.findByRole('button', { name: 'Sync Model Descriptions' }));
  await waitFor(() => expect(toast.success).toHaveBeenCalledWith('Synced 3 model(s). All stored descriptions are complete.'));
  expect(screen.getByRole('status')).toHaveTextContent('Checked 4 model(s). Synced 3 model(s). All stored descriptions are complete.');
  expect(mockFetch.mock.calls.slice(1)).toEqual([
    ['/api/admin/models/sync-descriptions?all_models=false&offset=0&limit=3', { method: 'POST' }],
    ['/api/admin/models/sync-descriptions?all_models=false&offset=3&limit=3', { method: 'POST' }],
  ]);
  expect(screen.getByRole('button', { name: 'Sync Model Descriptions' })).toBeEnabled();
});

it('stops after a failed batch and reports updates already completed', async () => {
  const log = jest.spyOn(console, 'error').mockImplementation(() => {});
  try {
    mockFetch.mockResolvedValueOnce(respond({}));
    mockFetch.mockResolvedValueOnce(respond({ updated_count: 2, total_models: 9, next_offset: 3 }));
    mockFetch.mockResolvedValueOnce(respond({ detail: 'Upstream unavailable' }, false));
    render(<AdminDashboardPage />);
    fireEvent.click(await screen.findByRole('button', { name: 'Sync Model Descriptions' }));
    await waitFor(() => expect(toast.error).toHaveBeenCalledWith('Upstream unavailable (2 model(s) updated before stopping)'));
    expect(screen.getByRole('status')).toHaveTextContent('Upstream unavailable (2 model(s) updated before stopping)');
    expect(mockFetch).toHaveBeenCalledTimes(3);
    expect(toast.success).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Sync Model Descriptions' })).toBeEnabled();
  } finally {
    log.mockRestore();
  }
});


it('reports incomplete descriptions after the final batch without claiming full completion', async () => {
  mockFetch.mockResolvedValueOnce(respond({}));
  mockFetch.mockResolvedValueOnce(respond({ updated_count: 1, total_models: 3, next_offset: null, remaining_incomplete: 2, incomplete_model_ids: ['example/first', 'example/second'] }));
  render(<AdminDashboardPage />);
  fireEvent.click(await screen.findByRole('button', { name: 'Sync Model Descriptions' }));
  await waitFor(() => expect(toast.warning).toHaveBeenCalledWith('Synced 1 model(s). 2 description(s) remain incomplete; retry sync to fetch missing full descriptions.'));
  expect(toast.success).not.toHaveBeenCalled();
  expect(screen.getByRole('status')).toHaveTextContent('Checked 3 model(s). Synced 1 model(s). 2 description(s) remain incomplete');
  fireEvent.click(screen.getByText('Models with incomplete descriptions'));
  expect(screen.getByText('example/first')).toBeVisible();
  expect(screen.getByText('example/second')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Sync Model Descriptions' })).toBeEnabled();
});
