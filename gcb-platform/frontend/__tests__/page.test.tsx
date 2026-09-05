/**
 * @jest-environment jsdom
 */
import { render, screen } from '@testing-library/react';
import Home from '@/app/page';

// Mock NextAuth
jest.mock('next-auth/react', () => ({
  useSession: () => ({
    data: null,
    status: 'unauthenticated',
  }),
}));

jest.mock('@/lib/api', () => ({
  apiClient: {
    getLeaderboard: jest.fn(() => new Promise(() => {})),
    getStats: jest.fn(() => new Promise(() => {})),
    getRecentTests: jest.fn(() => new Promise(() => {})),
  },
}));

jest.mock('@/components/home/GuardrailsAnimation', () => ({
  GuardrailsAnimation: () => null,
}));

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toHaveTextContent(/Evaluating AI for the\s*Great Commission/);
  });

  it('renders the description', () => {
    render(<Home />);
    const description = screen.getByText(/We measure which AI models meaningfully support gospel outreach/);
    expect(description).toBeInTheDocument();
  });

  it('links to the full recent tests page', () => {
    render(<Home />);
    expect(screen.getByRole('link', { name: /view all recent tests/i })).toHaveAttribute('href', '/recent-tests');
  });
});
