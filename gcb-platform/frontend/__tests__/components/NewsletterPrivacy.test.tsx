import { render } from "@testing-library/react";
import { GoogleAnalytics } from "@/components/analytics/GoogleAnalytics";
import { UmamiAnalytics } from "@/components/analytics/UmamiAnalytics";
import { HelpinatorWidget } from "@/components/helpinator/HelpinatorWidget";
import { readNewsletterActionToken } from "@/lib/newsletter-privacy";

let mockPath = "/";
jest.mock("next/navigation", () => ({ usePathname: () => mockPath }));
jest.mock("next/script", () => ({ __esModule: true, default: () => <span data-testid="external-script" /> }));
beforeEach(() => {
  process.env.NEXT_PUBLIC_UMAMI_SCRIPT_URL = "https://analytics.example.com/script.js";
  process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID = "test";
  process.env.NEXT_PUBLIC_HELPINATOR_HOST = "https://support.example.com";
  process.env.NEXT_PUBLIC_HELPINATOR_WIDGET_ID = "test";
});

test.each(["/newsletter/unsubscribe", "/newsletter/confirm", "/newsletter/confirm/"])("does not initialize third-party trackers on %s", (path) => {
  mockPath = path;
  const { container } = render(<><GoogleAnalytics /><UmamiAnalytics /><HelpinatorWidget /></>);
  expect(container).toBeEmptyDOMElement();
});

test("ordinary newsletter signup retains analytics and support", () => {
  mockPath = "/newsletter";
  const { getAllByTestId } = render(<><GoogleAnalytics /><UmamiAnalytics /><HelpinatorWidget /></>);
  expect(getAllByTestId("external-script")).toHaveLength(4);
});

test("takes the token out of the current history entry without a server action", () => {
  window.history.replaceState({ test: true }, "", "/newsletter/confirm?token=private-token&mode=email");
  expect(readNewsletterActionToken()).toBe("private-token");
  expect(window.location.search).toBe("?mode=email");
  expect(window.history.state).toEqual({ test: true });
});
