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

export type StepData = {
  order: number;
  type: string;
  title: string;
  content: { text: string };
};

export type ModuleData = {
  id: string;
  track_id: string;
  title: string;
  subtitle: string;
  level: string;
  level_order: number;
  duration_min: number;
  featured: boolean;
  accent: string;
  icon: string;
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
};
