import { render, screen } from '@testing-library/react';
import ModelPage from '@/app/leaderboard/models/[...id]/page';
import BlogPostPage from '@/app/insights/[slug]/page';
import type { ModelResponse } from '@/lib/api';
const mockGetModel = jest.fn();
jest.mock('@/app/leaderboard/models/model-data', () => ({ getModel: (...args: unknown[]) => mockGetModel(...args) }));
jest.mock('next/navigation', () => ({ usePathname: () => '/test', useSearchParams: () => new URLSearchParams(), useParams: () => ({ slug: 'example' }) }));
jest.mock('@/components/charts/CategoryChart', () => ({ CategoryChart: () => null }));
jest.mock('@/components/charts/RadarChart', () => ({ RadarChart: () => null }));
jest.mock('@/components/marketing/SocialShare', () => ({ SocialShare: () => null }));
jest.mock('react-markdown', () => ({ __esModule: true, default: ({ children }: { children: string }) => <p>{children}</p> }));
jest.mock('remark-gfm', () => ({ __esModule: true, default: jest.fn() }));
jest.mock('rehype-raw', () => ({ __esModule: true, default: jest.fn() }));
it.each([true, false])('includes newsletter offer on model page, active=%s', async is_active => {
  const model: ModelResponse = { id: 'test', model_id: 'test/model', name: 'Test model', provider: 'test', is_active, overall_score: 80 };
  mockGetModel.mockResolvedValue(model);
  render(await ModelPage({ params: Promise.resolve({ id: ['test', 'model'] }) }));
  expect(screen.getByRole('link', { name: 'Subscribe' })).toHaveAttribute('href', `/newsletter?source=${is_active ? 'model_results' : 'model_archived'}`);
});
it('renders both article offers without requiring article content edits', async () => {
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ title: 'Example insight', content: 'Article body', categories: [], published_at: '2026-09-08', updated_at: '2026-09-08' }) });
  render(<BlogPostPage />);
  expect(await screen.findByRole('heading', { name: 'Example insight' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Get the GCB digest' })).toHaveAttribute('href', '/newsletter?source=article_header');
  expect(screen.getByRole('link', { name: 'Subscribe' })).toHaveAttribute('href', '/newsletter?source=article_end');
});
