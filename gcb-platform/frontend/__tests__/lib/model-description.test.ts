/** @jest-environment node */
import { getFullModelDescription } from '@/lib/model-description';
const summary = 'A model for long-running tasks...';
const full = 'A model for long-running tasks, including extended reasoning.\n\nThe entire second paragraph is retained.';
const url = 'https://openrouter.ai/example/model';
const mockFetch = jest.fn();
function page(description = full, canonical = url) {
  return `<script type="application/ld+json">${JSON.stringify({ '@type': 'SoftwareApplication', url: canonical, description })}</script>`;
}
beforeEach(() => { mockFetch.mockReset(); global.fetch = mockFetch; });
it('recovers every paragraph from matching public model metadata', async () => {
  mockFetch.mockResolvedValue({ ok: true, text: async () => page() });
  expect(await getFullModelDescription('example/model', summary)).toBe(full);
  expect(mockFetch).toHaveBeenCalledWith(url, expect.objectContaining({ next: { revalidate: 86400 }, signal: expect.any(AbortSignal) }));
});
it.each([undefined, '', full])('does not fetch complete or absent descriptions: %s', async description => {
  expect(await getFullModelDescription('example/model', description)).toBe(description);
  expect(mockFetch).not.toHaveBeenCalled();
});
it.each([
  page('Unrelated longer description that does not continue the API summary.'),
  page(full, 'https://openrouter.ai/example/other-model'),
  page(full, 'https://unrelated.example/example/model'),
  page(summary),
  '<script type="application/ld+json">invalid json</script>',
  '<html>Unavailable</html>',
])('retains the original summary when full metadata cannot be verified', async html => {
  mockFetch.mockResolvedValue({ ok: true, text: async () => html });
  expect(await getFullModelDescription('example/model', summary)).toBe(summary);
});
it('tolerates source failures', async () => {
  mockFetch.mockRejectedValue(new Error('timeout'));
  expect(await getFullModelDescription('example/model', summary)).toBe(summary);
});
it('supports unicode ellipses and encoded variant IDs', async () => {
  mockFetch.mockResolvedValue({ ok: true, text: async () => page(full, url + ':free') });
  expect(await getFullModelDescription('example/model:free', 'A model for long-running tasks…')).toBe(full);
  expect(mockFetch.mock.calls[0][0]).toBe(url + '%3Afree');
});
