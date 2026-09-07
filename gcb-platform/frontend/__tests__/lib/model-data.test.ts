import { getModel } from "@/app/leaderboard/models/model-data";

jest.mock("react", () => ({ cache: (fn: unknown) => fn }));
jest.mock("next/navigation", () => ({
  notFound: () => { throw new Error("NEXT_NOT_FOUND"); },
}));

describe("model page lookup", () => {
  beforeEach(() => { global.fetch = jest.fn(); });

  it.each(["google/gemini-3-flash-preview", "google%2Fgemini-3-flash-preview"])(
    "resolves archived model URL %s", async id => {
      const model = { model_id: "google/gemini-3-flash-preview", is_active: false };
      (fetch as jest.Mock).mockResolvedValue({ ok: true, status: 200, json: async () => model });
      expect(await getModel(id)).toEqual(model);
      const url = new URL((fetch as jest.Mock).mock.calls[0][0]);
      expect(url.searchParams.get("model_id")).toBe(model.model_id);
    },
  );

  it("returns not found only for missing models", async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 404 });
    await expect(getModel("missing/model")).rejects.toThrow("NEXT_NOT_FOUND");
    (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 503 });
    await expect(getModel("google/model")).rejects.toThrow("Unable to load model details");
  });
});
