import { beforeEach, describe, expect, it, vi } from "vitest";
import type { TrpcContext } from "./_core/context";

vi.mock("./_core/llm", () => ({
  invokeLLM: vi.fn(async () => ({
    choices: [{ message: { content: "Uma variável é um nome que guarda um valor para você usar depois." } }],
  })),
}));

import { appRouter } from "./routers";
import { invokeLLM } from "./_core/llm";

describe("tutor.ask", () => {
  const ctx: TrpcContext = {
    user: null,
    req: {} as TrpcContext["req"],
    res: {} as TrpcContext["res"],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns a concise answer from the server-side tutor", async () => {
    const caller = appRouter.createCaller(ctx);
    const result = await caller.tutor.ask({
      message: "O que é uma variável?",
      subject: "informatica",
    });

    expect(result.answer).toContain("variável");
    expect(invokeLLM).toHaveBeenCalledTimes(1);
    expect(invokeLLM).toHaveBeenCalledWith(expect.objectContaining({
      messages: expect.arrayContaining([
        expect.objectContaining({ role: "user", content: "O que é uma variável?" }),
      ]),
    }));
  });

  it("rejects an empty question before calling the model", async () => {
    const caller = appRouter.createCaller(ctx);
    await expect(caller.tutor.ask({ message: "", subject: "matematica" })).rejects.toThrow();
    expect(invokeLLM).not.toHaveBeenCalled();
  });
});
