import { useEffect, useState } from "react";
import { Link, useParams } from "wouter";
import { api, type ModuleData, type StepData } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  BookOpen,
  Check,
  Clock3,
  Loader2,
  Sparkles,
  Star,
  Volume2,
} from "lucide-react";

const STEP_LABEL: Record<string, string> = {
  explanation: "Entender",
  example: "Exemplo",
  practice: "Praticar",
  check: "Verificar",
  next: "Próximo passo",
};

export default function Modulo() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [module, setModule] = useState<(ModuleData & { steps: StepData[] }) | null>(null);
  const [loading, setLoading] = useState(true);
  const [done, setDone] = useState<number[]>([]);
  const [favorite, setFavorite] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api
      .getModule(id)
      .then((m) => {
        setModule(m);
        const steps = m.steps || [];
        setDone([]);
      })
      .catch(() => toast.error("Não foi possível carregar o módulo."))
      .finally(() => setLoading(false));
    api.getFavorites().then((favs) => setFavorite(favs.includes(id))).catch(() => {});
  }, [id]);

  const total = module?.steps?.length || 0;

  const persist = async (completed: number) => {
    if (!module) return;
    const percent = total ? Math.round((completed / total) * 100) : 0;
    try {
      await api.saveProgress(module.id, percent);
    } catch {
      /* offline: mantém local */
    }
  };

  const toggleStep = (order: number) => {
    setDone((prev) => {
      const next = prev.includes(order) ? prev.filter((o) => o !== order) : [...prev, order];
      persist(next.length);
      return next;
    });
  };

  const finish = async () => {
    if (!module) return;
    setDone(module.steps.map((s) => s.order));
    await persist(total);
    toast.success("Módulo concluído!", { description: module.title });
  };

  const toggleFavorite = async () => {
    if (!module) return;
    try {
      const res = await api.toggleFavorite(module.id);
      setFavorite(res.favorited);
      toast(res.favorited ? "Adicionado aos favoritos" : "Removido dos favoritos");
    } catch {
      toast.error("Não foi possível atualizar o favorito.");
    }
  };

  const speak = (text: string) => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "pt-BR";
    u.rate = 0.94;
    window.speechSynthesis.speak(u);
  };

  const progress = total ? Math.round((done.length / total) * 100) : 0;

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-500">
        <Loader2 className="mr-2 animate-spin" size={20} /> Carregando módulo...
      </div>
    );
  }

  if (!module) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-20 text-center">
        <h1 className="text-2xl font-semibold text-slate-800">Módulo não encontrado</h1>
        <Link href="/" className="mt-4 inline-flex items-center gap-2 text-orange-600">
          <ArrowLeft size={16} /> Voltar ao início
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-5 py-8 sm:px-8">
      <div className="mb-6 flex items-center justify-between">
        <Link href="/" className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900">
          <ArrowLeft size={16} /> Voltar
        </Link>
        <button
          onClick={toggleFavorite}
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm ${
            favorite ? "border-amber-300 bg-amber-50 text-amber-700" : "border-slate-200 text-slate-600"
          }`}
        >
          <Star size={15} fill={favorite ? "currentColor" : "none"} />
          {favorite ? "Favorito" : "Favoritar"}
        </button>
      </div>

      <header className="mb-6">
        <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          <BookOpen size={13} /> {module.level} · <Clock3 size={13} /> {module.duration_min} min
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">{module.title}</h1>
        <p className="mt-2 text-slate-600">{module.subtitle}</p>
      </header>

      <div className="mb-6">
        <div className="mb-1 flex justify-between text-xs text-slate-500">
          <span>Progresso do módulo</span>
          <span>{progress}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-orange-500 transition-all" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <ol className="space-y-3">
        {module.steps.map((step) => {
          const isDone = done.includes(step.order);
          return (
            <li
              key={step.order}
              className={`rounded-xl border p-4 transition ${
                isDone ? "border-emerald-200 bg-emerald-50/60" : "border-slate-200 bg-white"
              }`}
            >
              <div className="flex items-start gap-3">
                <button
                  onClick={() => toggleStep(step.order)}
                  aria-label={`Marcar etapa ${step.order}`}
                  className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs ${
                    isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-slate-300 text-slate-400"
                  }`}
                >
                  {isDone ? <Check size={14} /> : step.order}
                </button>
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                      {STEP_LABEL[step.type] || step.type}
                    </span>
                    <span className="text-sm font-semibold text-slate-800">{step.title}</span>
                  </div>
                  <p className="text-sm leading-relaxed text-slate-700">{step.content?.text}</p>
                </div>
                <button
                  onClick={() => speak(step.content?.text || "")}
                  aria-label="Ouvir"
                  className="text-slate-400 hover:text-slate-700"
                >
                  <Volume2 size={16} />
                </button>
              </div>
            </li>
          );
        })}
      </ol>

      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <button
          onClick={finish}
          className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-orange-500 px-5 py-3 font-semibold text-white hover:bg-orange-600"
        >
          <Sparkles size={17} /> Concluir módulo
        </button>
        <Link
          href="/"
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-5 py-3 font-medium text-slate-700 hover:bg-slate-50"
        >
          Escolher outro módulo
        </Link>
      </div>
    </div>
  );
}
