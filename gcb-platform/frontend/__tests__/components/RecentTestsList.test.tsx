import { renderToStaticMarkup } from 'react-dom/server';
import { RecentTestsList } from '@/components/recent-tests/RecentTestsList';
import type { RecentTestItem } from '@/lib/api';

const item: RecentTestItem = {
  rank: 7,
  model: {
    id: 'model-uuid',
    name: 'Example Model',
    provider: 'example-provider',
    model_id: 'example-provider/example-model',
    description: 'A useful model description.',
  },
  test_run: {
    id: 'run-uuid',
    completed_at: '2026-09-04T12:00:00Z',
    question_set_version: '2.0',
  },
  score: 82.5,
  article: {
    id: 'article-uuid',
    title: 'Example review',
    slug: 'example-review',
  },
};

describe('RecentTestsList', () => {
  it('renders model data and encoded model/article links', () => {
    const html = renderToStaticMarkup(<RecentTestsList items={[item]} />);

    expect(html).toContain('Example Model');
    expect(html).toContain('#7');
    expect(html).toContain('82.5%');
    expect(html).toContain('Sep 4, 2026');
    expect(html).toContain('href="/leaderboard/models/example-provider%2Fexample-model"');
    expect(html).toContain('href="/insights/example-review"');
    expect(html).toContain('aria-label="Read Example review"');
  });

  it('does not render an article action when no article is associated', () => {
    const html = renderToStaticMarkup(<RecentTestsList items={[{ ...item, article: null }]} />);

    expect(html).not.toContain('aria-label="Read ');
  });

  it('renders empty and error states', () => {
    const empty = renderToStaticMarkup(<RecentTestsList items={[]} />);
    expect(empty).toContain('No completed tests are available yet.');

    const failed = renderToStaticMarkup(<RecentTestsList items={[]} error="Could not load tests." />);
    expect(failed).toContain('Could not load tests.');
  });
});
