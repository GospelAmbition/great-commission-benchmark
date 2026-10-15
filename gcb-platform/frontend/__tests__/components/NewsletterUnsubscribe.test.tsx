import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import UnsubscribePage from "@/app/newsletter/unsubscribe/page";

jest.mock("@/lib/api", () => ({ API_URL: "https://api.example.com" }));

beforeEach(() => {
  global.fetch = jest.fn();
  window.history.replaceState({}, "", "/newsletter/unsubscribe");
});

test("opening a signed link does not unsubscribe until the recipient clicks", async () => {
  window.history.replaceState({}, "", "/newsletter/unsubscribe?token=signed-token");
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true }) });
  render(<UnsubscribePage />);
  expect(fetch).not.toHaveBeenCalled();
  const button = screen.getByRole("button", { name: "Unsubscribe" });
  await waitFor(() => expect(button).toBeEnabled());
  fireEvent.click(button);
  await screen.findByText("Unsubscribe request saved");
  expect(JSON.parse((fetch as jest.Mock).mock.calls[0][1].body)).toEqual({ token: "signed-token" });
  expect((fetch as jest.Mock).mock.calls[0][1].method).toBe("POST");
});

test("invalid links offer email fallback without claiming an unsubscribe", async () => {
  window.history.replaceState({}, "", "/newsletter/unsubscribe?token=bad-token");
  (fetch as jest.Mock).mockResolvedValue({ ok: false, json: async () => ({ detail: "Invalid link" }) });
  render(<UnsubscribePage />);
  fireEvent.click(screen.getByRole("button", { name: "Unsubscribe" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Invalid link");
  expect(screen.queryByText("Unsubscribe request saved")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Use my email address instead" }));
  expect(screen.getByLabelText("Email address")).toBeInTheDocument();
});

test("email form works without a login or signed link", async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true }) });
  render(<UnsubscribePage />);
  fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "person@example.com" } });
  fireEvent.click(screen.getByRole("button", { name: "Unsubscribe" }));
  await screen.findByText("Unsubscribe request saved");
  expect(JSON.parse((fetch as jest.Mock).mock.calls[0][1].body)).toEqual({ email: "person@example.com" });
});
