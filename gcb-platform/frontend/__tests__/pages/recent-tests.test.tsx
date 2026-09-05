import { renderToStaticMarkup } from 'react-dom/server';
import Home from '@/app/page';
import RecentTestsPage from '@/app/recent-tests/page';

global.fetch = jest.fn();

describe('Recent Tests pages', () => {
  it('includes the five-item preview section and full-page link on the homepage', () => {
    const html = renderToStaticMarkup(<Home />);

    expect(html).toContain('Recent Tests');
    expect(html).toContain('href="/recent-tests"');
    expect(html).toContain('View all recent tests');
  });

  it('renders recent API results on the full page', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_version: '2.0',
        total: 1,
        items: [{
          rank: 3,
          model: {
            id: 'model-id',
            name: 'Newest Model',
            provider: 'provider',
            model_id: 'provider/newest',
            description: 'Newest description',
          },
          test_run: {
            id: 'run-id',
            completed_at: '2026-09-04T12:00:00Z',
            question_set_version: '2.0',
          },
          score: 88.4,
          article: null,
        }],
      }),
    });

    const page = await RecentTestsPage();
    const html = renderToStaticMarkup(page);

    expect(html).toContain('Newest Model');
    expect(html).toContain('88.4%');
    expect(html).toContain('#3');
    expect(html).toContain('Current benchmark version: 2.0');
  });
});
