/**
 * @jest-environment jsdom
 */
import { render, screen } from '@testing-library/react';
import LeaderboardPage from '@/app/leaderboard/page';
import { LeaderboardDataProvider } from '@/components/leaderboard/LeaderboardDataProvider';

jest.mock('@/components/home/GuardrailsAnimation', () => ({
  GuardrailsAnimation: () => null,
}));

jest.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams(),
}));

const initialData = {
  leaderboard: {
      items: [
        {
          id: 'test-model-uuid',
          model_id: 'test-model',
          model_name: 'Test Model',
          provider: 'Test Provider',
          overall_score: 85.5,
        },
      ],
      total: 1,
  },
  filter_options: {
    providers: ['Test Provider'],
    categories: [],
    trust_tiers: [],
    tiers: [],
    versions: [],
  },
};

function renderLeaderboard() {
  return render(
    <LeaderboardDataProvider initialData={initialData}>
      <LeaderboardPage />
    </LeaderboardDataProvider>
  );
}

describe('Leaderboard Page', () => {
  it('renders the page title', () => {
    renderLeaderboard();
    expect(screen.getByText('Leaderboard')).toBeInTheDocument();
  });

  it('displays leaderboard data', () => {
    renderLeaderboard();
    expect(screen.getByText('Test Model')).toBeInTheDocument();
  });

  it('shows filters', () => {
    renderLeaderboard();
    expect(screen.getByText('Filters')).toBeInTheDocument();
  });
});
