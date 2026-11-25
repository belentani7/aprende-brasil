export type TrackData = {
  id: string;
  label: string;
  eyebrow: string;
  description: string;
  color: string;
  icon: string;
  target_modules: number;
  module_count: number;
};

/**
 * Atividades interativas. Contrato retrocompatível: quem só lê `text` continua
 * funcionando, e cada atividade é opcional dentro de `content`.
 */
export type Activity =
  | {
      kind: "multiple-choice";
      id: string;
      prompt: string;
      options: string[];
      correctIndex: number;
      explanation: string;
    }
  | {
      kind: "true-false";
      id: string;
      prompt: string;
      answer: boolean;
      explanation: string;
    }
  | {
      kind: "fill-blank";
      id: string;
      prompt: string;
      acceptedAnswers: string[];
      explanation: string;
    }
  | {
      kind: "ordering";
      id: string;
      prompt: string;
      items: string[];
      correctOrder: number[];
    }
  | {
      kind: "matching";
      id: string;
      prompt: string;
      pairs: Array<{ left: string; right: string }>;
      explanation?: string;
    }
  | {
      kind: "numeric";
      id: string;
      prompt: string;
      answer: number;
      tolerance: number;
      explanation: string;
      unit?: string;
    };

export type VocabularyEntry = {
  term: string;
  definition: string;
  example?: string;
};

export type EducationalContent = {
  text: string;
  objectives?: string[];
  examples?: string[];
  activities?: Activity[];
  vocabulary?: VocabularyEntry[];
  references?: string[];
};

export type StepData = {
  order: number;
  type: string;
  title: string;
  content: EducationalContent;
};

export type ModuleData = {
  id: string;
  track_id: string;
  title: string;
  subtitle: string;
  level: string;
  level_order: number;
  duration_min: number;
  age_group?: string | null;
  objectives?: string | null;
  featured: boolean;
  accent: string;
  icon: string;
  /** Quantidade de etapas, presente no catálogo exportado (sempre 5). */
  step_count?: number;
  steps?: StepData[];
};

export type ModuleWithSteps = ModuleData & { steps: StepData[] };

export type ModulesResponse = {
  total: number;
  page: number;
  per_page: number;
  items: ModuleData[];
};

export type StatsData = {
  total_modules: number;
  started: number;
  completed: number;
  overall_percent: number;
};

export type TutorReply = {
  answer: string;
  source: string;
  module_id?: string | null;
};

/** Estado de uma atividade para o motor de recomendação. */
export type ActivityAttempt = {
  moduleId: string;
  activityId: string;
  correct: boolean;
  at: number;
};
