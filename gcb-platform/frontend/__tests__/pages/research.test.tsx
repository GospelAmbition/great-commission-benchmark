/**
 * @jest-environment jsdom
 */
import { render, screen, waitFor } from '@testing-library/react';
import ResearchPage from '@/app/research/page';

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

describe('Research Page', () => {
  it('renders the page title', () => {
    render(<ResearchPage />);
    expect(screen.getByText('Research')).toBeInTheDocument();
  });

  it('displays leaderboard data', async () => {
    render(<ResearchPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Model')).toBeInTheDocument();
    });
  });

  it('shows filters', () => {
    render(<ResearchPage />);
    expect(screen.getByText('Filters')).toBeInTheDocument();
  });
});
