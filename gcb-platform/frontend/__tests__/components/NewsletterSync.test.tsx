import { fireEvent, render, screen } from "@testing-library/react";
import { NewsletterSync } from "@/components/admin/NewsletterSync";

beforeEach(() => { global.fetch = jest.fn(); });

test("reports queued work without claiming the disabled worker completed it", async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ queued: 3, worker_enabled: false }) });
  const onQueued = jest.fn();
  render(<NewsletterSync pending={2} errors={1} enabled={false} lastSyncedAt={null} onQueued={onQueued} />);
  fireEvent.click(screen.getByRole("button", { name: "Retry pending syncs" }));
  expect(await screen.findByRole("status")).toHaveTextContent("3 subscribers queued. Automatic sync is disabled");
  expect(onQueued).toHaveBeenCalledTimes(1);
});

test("shows connection failure instead of success", async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, json: async () => ({ detail: "MailerLite returned HTTP 401" }) });
  render(<NewsletterSync pending={0} errors={0} enabled={true} lastSyncedAt={null} onQueued={jest.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: "Check connection" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("HTTP 401");
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
});
