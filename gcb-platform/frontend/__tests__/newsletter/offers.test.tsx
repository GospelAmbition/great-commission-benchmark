import { fireEvent, render, screen } from '@testing-library/react';
import { NewsletterButton, NewsletterOffer } from '@/components/marketing/NewsletterOffer';
import { trackEvent } from '@/lib/analytics';
let mockPathname = '/';
jest.mock('next/navigation', () => ({ usePathname: () => mockPathname, useSearchParams: () => new URLSearchParams() }));
jest.mock('@/lib/analytics', () => ({ trackEvent: jest.fn() }));
let onVisibility: IntersectionObserverCallback;
const disconnect = jest.fn();
beforeEach(() => {
  jest.clearAllMocks(); mockPathname = '/';
  window.IntersectionObserver = jest.fn(callback => {
    onVisibility = callback;
    return { observe: jest.fn(), disconnect, unobserve: jest.fn() };
  }) as unknown as typeof IntersectionObserver;
});
it('records visible impressions once, and again on navigation', () => {
  const { rerender } = render(<NewsletterButton source="header" />);
  const visible = [{ isIntersecting: true, intersectionRatio: 1 }] as IntersectionObserverEntry[];
  onVisibility(visible, {} as IntersectionObserver);
  onVisibility(visible, {} as IntersectionObserver);
  expect(trackEvent).toHaveBeenCalledTimes(1);
  mockPathname = '/insights';
  rerender(<NewsletterButton source="header" />);
  onVisibility(visible, {} as IntersectionObserver);
  expect(trackEvent).toHaveBeenCalledTimes(2);
});
it('links and tracks the originating offer', () => {
  render(<NewsletterOffer source="model_results" />);
  const link = screen.getByRole('link', { name: 'Subscribe' });
  expect(link).toHaveAttribute('href', '/newsletter?source=model_results');
  fireEvent.click(link);
  expect(trackEvent).toHaveBeenCalledWith('newsletter_cta_click', { source: 'model_results', path: '/' });
});
it('suppresses header and footer promotions on the signup page', () => {
  mockPathname = '/newsletter';
  render(<><NewsletterButton source="header" /><NewsletterOffer source="footer" /></>);
  expect(screen.queryByRole('link')).not.toBeInTheDocument();
  expect(screen.queryByRole('complementary')).not.toBeInTheDocument();
});
