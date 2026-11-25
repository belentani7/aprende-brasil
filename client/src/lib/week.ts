export type WeekDay = {
  /** Chave ISO (AAAA-MM-DD) usada no armazenamento local. */
  key: string;
  /** Rótulo curto em português: SEG, TER... */
  label: string;
  /** Dia do mês com dois dígitos. */
  day: string;
  /** Etapas concluídas nesse dia. */
  steps: number;
  isToday: boolean;
};

const LABELS = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"];

export function isoDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/**
 * Últimos sete dias, terminando hoje, com a atividade real registrada.
 * Recebe `today` para ser determinístico nos testes.
 */
export function buildWeek(
  today: Date,
  counts: Record<string, number> = {}
): WeekDay[] {
  const days: WeekDay[] = [];
  for (let offset = 6; offset >= 0; offset -= 1) {
    const date = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() - offset
    );
    const key = isoDate(date);
    const value = counts[key];
    days.push({
      key,
      label: LABELS[date.getDay()],
      day: String(date.getDate()).padStart(2, "0"),
      steps: Number.isFinite(value) ? Math.max(0, value) : 0,
      isToday: offset === 0,
    });
  }
  return days;
}

export function streak(counts: Record<string, number>, today: Date): number {
  let total = 0;
  for (let offset = 0; offset < 365; offset += 1) {
    const date = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() - offset
    );
    const value = counts[isoDate(date)] ?? 0;
    if (value <= 0) break;
    total += 1;
  }
  return total;
}
