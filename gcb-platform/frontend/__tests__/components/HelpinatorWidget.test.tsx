/**
 * @jest-environment jsdom
 */
import { render } from '@testing-library/react';
import { HelpinatorWidget } from '@/components/helpinator/HelpinatorWidget';

let mockPathname = '/';
jest.mock('next/navigation', () => ({
  usePathname: () => mockPathname,
}));

jest.mock('next/script', () => ({
  __esModule: true,
  default: (props: { src: string }) => <div data-testid="helpinator-script" data-src={props.src} />,
}));

const ORIGINAL_ENV = process.env;

describe('HelpinatorWidget', () => {
  beforeEach(() => {
    mockPathname = '/';
    process.env = {
      ...ORIGINAL_ENV,
      NEXT_PUBLIC_HELPINATOR_HOST: 'https://apps.example.org',
      NEXT_PUBLIC_HELPINATOR_WIDGET_ID: 'widget-123',
    };
  });

  afterAll(() => {
    process.env = ORIGINAL_ENV;
  });

  it('renders the widget and script on public pages', () => {
    const { container } = render(<HelpinatorWidget />);
    const widget = container.querySelector('helpinator-widget');
    expect(widget).toHaveAttribute('host', 'https://apps.example.org');
    expect(widget).toHaveAttribute('widget-id', 'widget-123');
    expect(container.querySelector('[data-testid=helpinator-script]')).toHaveAttribute(
      'data-src',
      'https://apps.example.org/js/helpinator-widget.iife.js'
    );
  });

  it.each(['/admin', '/admin/users', '/blog-manager/new', '/moderator', '/dashboard', '/profile', '/runner'])(
    'renders nothing on %s',
    (path) => {
      mockPathname = path;
      const { container } = render(<HelpinatorWidget />);
      expect(container).toBeEmptyDOMElement();
    }
  );

  it('still renders on paths that only share a prefix', () => {
    mockPathname = '/profiles-of-faith';
    const { container } = render(<HelpinatorWidget />);
    expect(container.querySelector('helpinator-widget')).not.toBeNull();
  });

  it('renders nothing when env vars are missing', () => {
    delete process.env.NEXT_PUBLIC_HELPINATOR_WIDGET_ID;
    const { container } = render(<HelpinatorWidget />);
    expect(container).toBeEmptyDOMElement();
  });
});
