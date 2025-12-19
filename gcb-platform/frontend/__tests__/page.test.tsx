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

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toHaveTextContent('Great Commission Benchmark');
  });

  it('renders the description', () => {
    render(<Home />);
    const description = screen.getByText(/Evaluating LLMs on their ability to support Great Commission Christians/);
    expect(description).toBeInTheDocument();
  });

  it('shows login button when user is not authenticated', () => {
    render(<Home />);
    const loginButton = screen.getByRole('link', { name: /login/i });
    expect(loginButton).toBeInTheDocument();
  });
});
