import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { NewsletterCampaignSends } from "@/components/admin/NewsletterCampaignSends";

const send = { id: "send-1", post_title: "Monthly update", audience: "production", status: "uncertain", provider: "mailerlite", campaign_id: "campaign-1", recipient_count: 4, error_message: "Schedule outcome uncertain", created_at: "2026-10-14T12:00:00Z" };
const response = (data: unknown, ok = true) => ({ ok, json: async () => data });
beforeEach(() => { global.fetch = jest.fn(); });

test("checks an uncertain send without invoking the sending endpoint", async () => {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ items: [send] }))
    .mockResolvedValueOnce(response({ status: "sent" }))
    .mockResolvedValueOnce(response({ items: [{ ...send, status: "sent", error_message: null }] }));
  render(<NewsletterCampaignSends />);
  expect(await screen.findByText("Schedule outcome uncertain")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Check status" }));
  expect(await screen.findByText("sent")).toBeInTheDocument();
  expect(fetch).toHaveBeenNthCalledWith(2, "/api/admin/newsletter/sends/send-1/refresh", { method: "POST" });
  expect(screen.queryByRole("button", { name: "Check status" })).not.toBeInTheDocument();
});

test("retains uncertainty when the provider status cannot be verified", async () => {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ items: [send] }))
    .mockResolvedValueOnce(response({ detail: "MailerLite returned HTTP 503" }, false));
  render(<NewsletterCampaignSends />);
  fireEvent.click(await screen.findByRole("button", { name: "Check status" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("HTTP 503");
  expect(screen.getByText("uncertain")).toBeInTheDocument();
  await waitFor(() => expect(screen.getByRole("button", { name: "Check status" })).toBeEnabled());
});
