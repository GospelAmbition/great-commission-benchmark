/**
 * @jest-environment jsdom
 */
import { render, screen } from '@testing-library/react';
import Home from '@/app/(home)/page';

// Mock NextAuth
jest.mock('next-auth/react', () => ({
  useSession: () => ({
    data: null,
    status: 'unauthenticated',
  }),
}));

jest.mock('@/lib/api', () => ({
  apiClient: {
    getLeaderboard: jest.fn(async () => ({ items: [], total: 0 })),
    getStats: jest.fn(async () => null),
    getRecentTests: jest.fn(async () => ({ items: [] })),
  },
}));

jest.mock('@/components/home/GuardrailsAnimation', () => ({
  GuardrailsAnimation: () => null,
}));

describe('Home Page', () => {
  it('renders the main heading', async () => {
    render(await Home());
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toHaveTextContent(/Evaluating AI for the\s*Great Commission/);
  });

  it('renders the description', async () => {
    render(await Home());
    const description = screen.getByText(/We measure which AI models meaningfully support gospel outreach/);
    expect(description).toBeInTheDocument();
  });

  it('links to the full recent tests page', async () => {
    render(await Home());
    expect(screen.getByRole('link', { name: /view all recent tests/i })).toHaveAttribute('href', '/recent-tests');
  });
});
