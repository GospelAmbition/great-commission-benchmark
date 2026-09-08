import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import NewsletterPage from '@/app/newsletter/page';
import { trackEvent, trackNewsletterSignup } from '@/lib/analytics';
import { toast } from 'sonner';

jest.mock('next-auth/react', () => ({ useSession: () => ({ data: null }) }));
jest.mock('@/components/recaptcha/RecaptchaScript', () => ({ RecaptchaScript: () => null }));
const mockExecute = jest.fn();
jest.mock('@/hooks/useRecaptcha', () => ({ useRecaptcha: () => ({ executeRecaptcha: mockExecute }) }));
jest.mock('@/lib/analytics', () => ({ trackEvent: jest.fn(), trackNewsletterSignup: jest.fn() }));
jest.mock('sonner', () => ({ toast: { success: jest.fn(), error: jest.fn() } }));
const mockFetch = jest.fn();
const originalKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = mockFetch;
  delete process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
  window.history.replaceState({}, '', '/newsletter?source=article_end');
});
afterAll(() => {
  if (originalKey === undefined) delete process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
  else process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY = originalKey;
});
function submit(email = 'reader@example.com') {
  fireEvent.change(screen.getByLabelText('Email Address'), { target: { value: email } });
  fireEvent.submit(screen.getByRole('button', { name: 'Subscribe to Newsletter' }).closest('form')!);
}
it.each([
  ['Successfully subscribed to newsletter', 'subscribed', 'Successfully subscribed!'],
  ['Email already subscribed', 'already_subscribed', 'You’re already subscribed!'],
  ['Subscription reactivated', 'reactivated', 'Your subscription is active again!'],
])('handles %s and attributes the accepted submission', async (message, outcome, heading) => {
  mockFetch.mockResolvedValue({ ok: true, json: async () => ({ success: true, message }) });
  render(<NewsletterPage />);
  submit(' reader@example.com ');
  expect(await screen.findByRole('status')).toHaveTextContent(heading);
  expect(trackNewsletterSignup).toHaveBeenCalledWith('article_end');
  expect(trackEvent).toHaveBeenCalledWith('newsletter_signup_outcome', { source: 'article_end', outcome });
  expect(JSON.parse(mockFetch.mock.calls[0][1].body).email).toBe('reader@example.com');
  expect(JSON.stringify((trackEvent as jest.Mock).mock.calls)).not.toContain('reader@example.com');
});
it('rejects invalid email without a request', () => {
  render(<NewsletterPage />); submit('invalid');
  expect(mockFetch).not.toHaveBeenCalled();
  expect(toast.error).toHaveBeenCalledWith('Please enter a valid email address');
});
it('retains email and allows retry after network failure', async () => {
  mockFetch.mockRejectedValueOnce(new Error('Network unavailable'));
  render(<NewsletterPage />); submit();
  await waitFor(() => expect(toast.error).toHaveBeenCalledWith('Network unavailable'));
  expect(screen.getByLabelText('Email Address')).toHaveValue('reader@example.com');
  expect(screen.getByRole('button', { name: 'Subscribe to Newsletter' })).toBeEnabled();
});
it('blocks concurrent submissions', async () => {
  let resolve!: (value: unknown) => void;
  mockFetch.mockReturnValue(new Promise(r => { resolve = r; }));
  render(<NewsletterPage />); submit();
  fireEvent.submit(screen.getByLabelText('Email Address').closest('form')!);
  expect(mockFetch).toHaveBeenCalledTimes(1);
  resolve({ ok: true, json: async () => ({ success: true }) });
  await screen.findByRole('status');
});
it('handles backend security failure without a conversion', async () => {
  mockFetch.mockResolvedValue({ ok: false, json: async () => ({ detail: 'reCAPTCHA verification failed' }) });
  render(<NewsletterPage />); submit();
  await waitFor(() => expect(trackEvent).toHaveBeenCalledWith('newsletter_signup_outcome', { source: 'article_end', outcome: 'security_error' }));
  expect(trackNewsletterSignup).not.toHaveBeenCalled();
  expect(screen.getByLabelText('Email Address')).toHaveValue('reader@example.com');
});
it('passes a configured security token', async () => {
  process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY = 'test-site-key';
  mockExecute.mockResolvedValue('test-token');
  mockFetch.mockResolvedValue({ ok: true, json: async () => ({ success: true }) });
  render(<NewsletterPage />); submit();
  await screen.findByRole('status');
  expect(JSON.parse(mockFetch.mock.calls[0][1].body).recaptcha_token).toBe('test-token');
});
it('falls back to direct-page attribution for unrecognized sources', async () => {
  window.history.replaceState({}, '', '/newsletter?source=someone@example.com');
  mockFetch.mockResolvedValue({ ok: true, json: async () => ({ success: true }) });
  render(<NewsletterPage />); submit();
  await screen.findByRole('status');
  expect(trackNewsletterSignup).toHaveBeenCalledWith('newsletter_page');
});
