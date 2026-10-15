import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TextDecoder } from "util";
import { NewsletterImport } from "@/components/admin/NewsletterImport";

jest.mock("sonner", () => ({ toast: { success: jest.fn() } }));

const preview = {
  dry_run: true, batch_id: null, total_rows: 1, counts: { create_active: 1 },
  rows: [{ row: 2, email: "person@example.com", action: "create_active", message: "Add subscriber" }],
  rows_truncated: false, requires_consent: true, message: "Preview only; no changes saved",
};

beforeEach(() => {
  Object.defineProperty(global, "TextDecoder", { value: TextDecoder, configurable: true });
  global.fetch = jest.fn();
});

async function openAndLoad() {
  fireEvent.click(screen.getByRole("button", { name: "Import CSV" }));
  const contents = Buffer.from("email\nperson@example.com\n", "utf-8");
  const file = new File([], "subscribers.csv", { type: "text/csv" });
  Object.defineProperty(file, "arrayBuffer", { value: async () => contents });
  fireEvent.change(screen.getByLabelText(/CSV file/), { target: { files: [file] } });
  fireEvent.change(screen.getByLabelText("Subscriber source"), { target: { value: "Google Forms" } });
  await waitFor(() => expect(screen.getByRole("button", { name: "Preview import" })).toBeEnabled());
}

test("requires preview and consent before applying, then refreshes the list", async () => {
  const onImported = jest.fn();
  (fetch as jest.Mock).mockResolvedValueOnce({ ok: true, json: async () => preview });
  (fetch as jest.Mock).mockResolvedValueOnce({ ok: true, json: async () => ({ ...preview, dry_run: false, batch_id: "batch-1", message: "Import saved" }) });
  render(<NewsletterImport onImported={onImported} />);
  await openAndLoad();
  expect(screen.queryByRole("button", { name: "Import valid rows" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Preview import" }));
  await screen.findByText("Preview only; no changes saved");
  const apply = screen.getByRole("button", { name: "Import valid rows" });
  expect(apply).toBeDisabled();
  fireEvent.change(screen.getByLabelText("How did these people subscribe?"), { target: { value: "Newsletter opt-in" } });
  fireEvent.click(screen.getByRole("checkbox"));
  expect(apply).toBeEnabled();
  fireEvent.click(apply);
  await waitFor(() => expect(onImported).toHaveBeenCalledTimes(1));
  const body = JSON.parse((fetch as jest.Mock).mock.calls[1][1].body);
  expect(body).toMatchObject({ dry_run: false, confirm_subscribed: true, consent_note: "Newsletter opt-in", source: "Google Forms" });
  expect(screen.queryByRole("button", { name: "Import valid rows" })).not.toBeInTheDocument();
});

test("changing the source invalidates a preview", async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => preview });
  render(<NewsletterImport onImported={jest.fn()} />);
  await openAndLoad();
  fireEvent.click(screen.getByRole("button", { name: "Preview import" }));
  await screen.findByText("Preview only; no changes saved");
  fireEvent.change(screen.getByLabelText("Subscriber source"), { target: { value: "Previous newsletter" } });
  expect(screen.queryByRole("button", { name: "Import valid rows" })).not.toBeInTheDocument();
});

test("shows server validation errors without claiming success", async () => {
  const onImported = jest.fn();
  (fetch as jest.Mock).mockResolvedValue({ ok: false, json: async () => ({ detail: "No email column found" }) });
  render(<NewsletterImport onImported={onImported} />);
  await openAndLoad();
  fireEvent.click(screen.getByRole("button", { name: "Preview import" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("No email column found");
  expect(onImported).not.toHaveBeenCalled();
});
