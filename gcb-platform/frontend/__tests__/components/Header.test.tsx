/**
 * @jest-environment jsdom
 */
import { fireEvent, render, screen } from '@testing-library/react';
import { Header } from '@/components/layout/Header';

// Mock NextAuth
jest.mock('next-auth/react', () => ({
  useSession: () => ({
    data: null,
    status: 'unauthenticated',
  }),
  signOut: jest.fn(),
}));

jest.mock('next/navigation', () => ({
  usePathname: () => '/',
  useRouter: () => ({ push: jest.fn() }),
}));

jest.mock('@/lib/useUserProfile', () => ({
  useUserProfile: () => ({
    isAdmin: false,
    isModerator: false,
    canViewBenchmark: false,
    canModerate: false,
    canManageBlog: false,
    canAdmin: false,
  }),
}));

describe('Header Component', () => {
  it('renders the logo', () => {
    render(<Header />);
    const logo = screen.getByText('Great Commission Benchmark');
    expect(logo).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    render(<Header />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Leaderboard')).toBeInTheDocument();
    expect(screen.getByText('Recent Tests')).toBeInTheDocument();
    expect(screen.getByText('Insights')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
  });

  it('shows login button when user is not authenticated', () => {
    render(<Header />);
    const loginButton = screen.getByRole('link', { name: /login/i });
    expect(loginButton).toBeInTheDocument();
  });

  it('includes Recent Tests in the mobile navigation', () => {
    render(<Header />);
    fireEvent.click(screen.getByRole('button', { name: /open navigation menu/i }));

    expect(screen.getByRole('link', { name: 'Recent Tests' })).toHaveClass('text-base');
  });
});
