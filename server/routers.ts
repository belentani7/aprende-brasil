import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { invokeLLM } from "./_core/llm";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { z } from "zod";

const subjectLabels = {
  informatica: "informática",
  matematica: "matemática",
  idiomas: "idiomas",
} as const;

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),
  tutor: router({
    ask: publicProcedure
      .input(z.object({
        message: z.string().min(1).max(800),
        subject: z.enum(["informatica", "matematica", "idiomas"]),
      }))
      .mutation(async ({ input }) => {
        const response = await invokeLLM({
          messages: [
            {
              role: "system",
              content: `Você é Nilo, o tutor da Aprende Brasil. Responda em português brasileiro, com tom acolhedor, curioso e objetivo. A pessoa está estudando ${subjectLabels[input.subject]}. Explique uma ideia por vez, use exemplos concretos, faça no máximo uma pergunta de acompanhamento e nunca entregue uma resposta que substitua o raciocínio do aluno. Se for um exercício, ofereça uma pista antes da solução. Não invente progresso, notas ou informações pessoais. Mantenha a resposta em até 120 palavras.`,
            },
            { role: "user", content: input.message },
          ],
        });
        const content = response.choices?.[0]?.message?.content;
        if (typeof content === "string" && content.trim()) return { answer: content.trim() };
        if (Array.isArray(content)) {
          const text = content.find((item) => item.type === "text")?.text;
          if (text) return { answer: text.trim() };
        }
        return { answer: "Vamos explorar isso juntos: qual parte do tema parece mais difícil para você agora?" };
      }),
  }),
});

export type AppRouter = typeof appRouter;
