/**
 * @jest-environment jsdom
 */
import { render, screen, waitFor } from '@testing-library/react';
import LeaderboardPage from '@/app/leaderboard/page';

// Mock API client
jest.mock('@/lib/api', () => ({
  apiClient: {
    getLeaderboard: jest.fn().mockResolvedValue({
      items: [
        {
          model_id: 'test-model',
          model_name: 'Test Model',
          provider: 'Test Provider',
          overall_score: 85.5,
        },
      ],
      total: 1,
    }),
  },
}));

describe('Leaderboard Page', () => {
  it('renders the page title', () => {
    render(<LeaderboardPage />);
    expect(screen.getByText('Leaderboard')).toBeInTheDocument();
  });

  it('displays leaderboard data', async () => {
    render(<LeaderboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Model')).toBeInTheDocument();
    });
  });

  it('shows filters', () => {
    render(<LeaderboardPage />);
    expect(screen.getByText('Filters')).toBeInTheDocument();
  });
});
