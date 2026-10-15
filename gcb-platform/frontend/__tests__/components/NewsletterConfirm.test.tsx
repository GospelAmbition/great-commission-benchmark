import { fireEvent, render, screen } from "@testing-library/react";
import ConfirmNewsletterPage from "@/app/newsletter/confirm/page";

jest.mock("@/lib/api", () => ({ API_URL: "https://api.example.com" }));

beforeEach(() => {
  global.fetch = jest.fn();
  window.history.replaceState({}, "", "/newsletter/confirm?token=signed-confirmation");
});

test("confirmation needs a click and reports pending verification", async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ message: "Confirmed; verification pending" }) });
  render(<ConfirmNewsletterPage />);
  expect(fetch).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Confirm resubscription" }));
  expect(await screen.findByRole("status")).toHaveTextContent("Confirmed; verification pending");
  expect(JSON.parse((fetch as jest.Mock).mock.calls[0][1].body)).toEqual({ token: "signed-confirmation" });
});

test("expired confirmation does not show success", async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, json: async () => ({ detail: "Confirmation expired" }) });
  render(<ConfirmNewsletterPage />);
  fireEvent.click(screen.getByRole("button", { name: "Confirm resubscription" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Confirmation expired");
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
});
