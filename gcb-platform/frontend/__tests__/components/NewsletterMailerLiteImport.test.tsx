import { fireEvent, render, screen } from "@testing-library/react";
import { NewsletterMailerLiteImport } from "@/components/admin/NewsletterMailerLiteImport";

const preview = { snapshot_sha256: "a".repeat(64), group_id: "prod", total_rows: 2, requires_consent: true, counts: { create_active: 1, create_unsubscribed: 1 }, remote_status_counts: { active: 1, bounced: 1 }, rows: [], rows_truncated: false };
const response = (data: unknown, ok = true) => ({ ok, json: async () => data });
beforeEach(() => { global.fetch = jest.fn(); });

test("requires preview and consent and applies only the reviewed snapshot", async () => {
  (fetch as jest.Mock).mockResolvedValueOnce(response(preview)).mockResolvedValueOnce(response({ message: "Saved and queued" }));
  const onImported = jest.fn();
  render(<NewsletterMailerLiteImport onImported={onImported} />);
  expect(screen.queryByText("Import reviewed contacts")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Preview MailerLite import" }));
  expect(await screen.findByRole("button", { name: "Import reviewed contacts" })).toBeDisabled();
  fireEvent.click(screen.getByRole("checkbox"));
  expect(screen.getByRole("button", { name: "Import reviewed contacts" })).toBeDisabled();
  fireEvent.change(screen.getByLabelText("How did these contacts subscribe?"), { target: { value: "Legacy newsletter form" } });
  fireEvent.click(screen.getByRole("button", { name: "Import reviewed contacts" }));
  expect(await screen.findByRole("status")).toHaveTextContent("Saved and queued");
  expect(JSON.parse((fetch as jest.Mock).mock.calls[1][1].body)).toEqual({ dry_run: false, snapshot_sha256: preview.snapshot_sha256, confirm_subscribed: true, consent_note: "Legacy newsletter form" });
  expect(onImported).toHaveBeenCalledTimes(1);
});

test("invalidates a changed snapshot instead of allowing repeated apply", async () => {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ ...preview, requires_consent: false }))
    .mockResolvedValueOnce(response({ detail: "Contacts changed; preview again" }, false));
  render(<NewsletterMailerLiteImport onImported={jest.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: "Preview MailerLite import" }));
  fireEvent.click(await screen.findByRole("button", { name: "Import reviewed contacts" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Contacts changed");
  expect(screen.queryByRole("button", { name: "Import reviewed contacts" })).not.toBeInTheDocument();
});
