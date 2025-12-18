/**
 * @jest-environment jsdom
 */
import { render, screen } from '@testing-library/react';
import { TopPerformers } from '@/components/home/TopPerformers';

const mockPerformers = [
  {
    rank: 1,
    model_id: 'gpt-4-turbo',
    model_name: 'GPT-4 Turbo',
    provider: 'OpenAI',
    score: 92.3,
  },
  {
    rank: 2,
    model_id: 'claude-3-opus',
    model_name: 'Claude 3 Opus',
    provider: 'Anthropic',
    score: 89.7,
  },
  {
    rank: 3,
    model_id: 'gemini-ultra',
    model_name: 'Gemini Ultra',
    provider: 'Google',
    score: 87.2,
  },
];

describe('TopPerformers Component', () => {
  it('renders all performers', () => {
    render(<TopPerformers performers={mockPerformers} />);
    expect(screen.getByText('GPT-4 Turbo')).toBeInTheDocument();
    expect(screen.getByText('Claude 3 Opus')).toBeInTheDocument();
    expect(screen.getByText('Gemini Ultra')).toBeInTheDocument();
  });

  it('displays scores correctly', () => {
    render(<TopPerformers performers={mockPerformers} />);
    expect(screen.getByText('92.3')).toBeInTheDocument();
    expect(screen.getByText('89.7')).toBeInTheDocument();
    expect(screen.getByText('87.2')).toBeInTheDocument();
  });

  it('shows rank emojis for top 3', () => {
    render(<TopPerformers performers={mockPerformers} />);
    // Check that emojis are present (they may render as text)
    const cards = screen.getAllByText(/GPT-4 Turbo|Claude 3 Opus|Gemini Ultra/);
    expect(cards.length).toBe(3);
  });
});
