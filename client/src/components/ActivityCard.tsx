import { useMemo, useState } from "react";
import {
  ACTIVITY_LABEL,
  evaluateChoice,
  isAnswerAccepted,
  isMatchingCorrect,
  isNumericCorrect,
  isOrderCorrect,
  parseNumberInput,
  resultFor,
  shuffleStable,
  type ActivityResult,
} from "@/lib/activities";
import { Check, RotateCcw, X } from "lucide-react";
import type { Activity } from "@/lib/types";

type Props = {
  activity: Activity;
  onResult?: (result: ActivityResult) => void;
};

const HINTS: Record<Activity["kind"], string> = {
  "multiple-choice": "Escolha uma opção. Você pode errar quantas vezes quiser.",
  "true-false": "Decida se a frase é verdadeira ou falsa.",
  "fill-blank":
    "Escreva só a palavra que falta. Acentuação e maiúsculas não contam.",
  ordering: "Use as setas para mover cada item até a ordem correta.",
  matching: "Escolha o item da esquerda e depois o par certo à direita.",
  numeric: "Use vírgula ou ponto para decimais. Confira a unidade pedida.",
};

export default function ActivityCard({ activity, onResult }: Props) {
  return (
    <div className="activity-card" data-activity-id={activity.id}>
      <div className="activity-head">
        <span className="activity-kind">{ACTIVITY_LABEL[activity.kind]}</span>
        <p className="activity-prompt">{activity.prompt}</p>
      </div>
      <p className="activity-hint">{HINTS[activity.kind]}</p>
      {activity.kind === "multiple-choice" && (
        <ChoiceActivity activity={activity} onResult={onResult} />
      )}
      {activity.kind === "true-false" && (
        <ChoiceActivity
          activity={activity}
          onResult={onResult}
          options={["Verdadeiro", "Falso"]}
        />
      )}
      {activity.kind === "fill-blank" && (
        <FillBlankActivity activity={activity} onResult={onResult} />
      )}
      {activity.kind === "ordering" && (
        <OrderingActivity activity={activity} onResult={onResult} />
      )}
      {activity.kind === "matching" && (
        <MatchingActivity activity={activity} onResult={onResult} />
      )}
      {activity.kind === "numeric" && (
        <NumericActivity activity={activity} onResult={onResult} />
      )}
    </div>
  );
}

function Feedback({ result }: { result: ActivityResult }) {
  return (
    <p
      className={`activity-feedback ${result.correct ? "is-correct" : "is-wrong"}`}
      role="status"
      aria-live="polite"
    >
      {result.correct ? (
        <Check size={15} aria-hidden="true" />
      ) : (
        <X size={15} aria-hidden="true" />
      )}
      <span>{result.feedback}</span>
    </p>
  );
}

function ChoiceActivity({
  activity,
  onResult,
  options,
}: Props & { options?: string[] }) {
  const choices =
    activity.kind === "multiple-choice" ? activity.options : (options ?? []);
  const [picked, setPicked] = useState<number | null>(null);
  const [result, setResult] = useState<ActivityResult | null>(null);

  const choose = (index: number) => {
    setPicked(index);
    const next = evaluateChoice(activity, index);
    setResult(next);
    onResult?.(next);
  };

  return (
    <div>
      <div
        className="activity-options"
        role="group"
        aria-label="Opções de resposta"
      >
        {choices.map((option, index) => {
          const state =
            picked === null
              ? "idle"
              : activity.kind === "multiple-choice" &&
                  index === activity.correctIndex
                ? "correct"
                : index === picked
                  ? "wrong"
                  : "idle";
          return (
            <button
              key={option + index}
              type="button"
              className="activity-option"
              data-state={state}
              aria-pressed={picked === index}
              onClick={() => choose(index)}
            >
              <span className="activity-option-mark" aria-hidden="true">
                {String.fromCharCode(65 + index)}
              </span>
              {option}
            </button>
          );
        })}
      </div>
      {result && <Feedback result={result} />}
    </div>
  );
}

function FillBlankActivity({ activity, onResult }: Props) {
  const [value, setValue] = useState("");
  const [result, setResult] = useState<ActivityResult | null>(null);

  const check = (event: React.FormEvent) => {
    event.preventDefault();
    if (!value.trim()) return;
    const next = resultFor(
      activity,
      activity.kind === "fill-blank" && isAnswerAccepted(activity, value)
    );
    setResult(next);
    onResult?.(next);
  };

  return (
    <form className="activity-form" onSubmit={check}>
      <label htmlFor={`${activity.id}-input`} className="sr-only">
        Sua resposta
      </label>
      <input
        id={`${activity.id}-input`}
        className="activity-input"
        value={value}
        onChange={event => {
          setValue(event.target.value);
          setResult(null);
        }}
        autoComplete="off"
        spellCheck={false}
        placeholder="Escreva a palavra"
      />
      <button type="submit" className="activity-check">
        Conferir
      </button>
      {result && <Feedback result={result} />}
    </form>
  );
}

function NumericActivity({ activity, onResult }: Props) {
  const [value, setValue] = useState("");
  const [result, setResult] = useState<ActivityResult | null>(null);
  const unit =
    activity.kind === "numeric" && activity.unit ? activity.unit : "";

  const check = (event: React.FormEvent) => {
    event.preventDefault();
    const parsed = parseNumberInput(value);
    if (!Number.isFinite(parsed)) return;
    const next = resultFor(activity, isNumericCorrect(activity, parsed));
    setResult(next);
    onResult?.(next);
  };

  return (
    <form className="activity-form" onSubmit={check}>
      <label htmlFor={`${activity.id}-numeric`} className="sr-only">
        Resposta numérica
      </label>
      <div className="activity-numeric">
        <input
          id={`${activity.id}-numeric`}
          className="activity-input activity-input--short"
          value={value}
          inputMode="decimal"
          onChange={event => {
            setValue(event.target.value);
            setResult(null);
          }}
          placeholder="0"
        />
        {unit && <span className="activity-unit">{unit}</span>}
      </div>
      <button type="submit" className="activity-check">
        Conferir
      </button>
      {result && <Feedback result={result} />}
    </form>
  );
}

function OrderingActivity({ activity, onResult }: Props) {
  const initial = useMemo(() => {
    if (activity.kind !== "ordering") return [] as number[];
    const indices = activity.items.map((_, index) => index);
    // Embaralha de forma estável (mesma ordem em toda visita) para a pessoa
    // poder voltar e comparar.
    const shuffled = shuffleStable(indices, activity.id);
    return shuffled.every((value, index) => value === index)
      ? [...indices].reverse()
      : shuffled;
  }, [activity]);

  const [order, setOrder] = useState<number[]>(initial);
  const [result, setResult] = useState<ActivityResult | null>(null);

  if (activity.kind !== "ordering") return null;

  const move = (position: number, direction: -1 | 1) => {
    const target = position + direction;
    if (target < 0 || target >= order.length) return;
    const next = [...order];
    [next[position], next[target]] = [next[target], next[position]];
    setOrder(next);
    setResult(null);
  };

  const check = () => {
    const next = resultFor(activity, isOrderCorrect(activity, order));
    setResult(next);
    onResult?.(next);
  };

  return (
    <div>
      <ol className="activity-order">
        {order.map((itemIndex, position) => (
          <li key={itemIndex} className="activity-order-item">
            <span className="activity-order-number" aria-hidden="true">
              {position + 1}
            </span>
            <span className="activity-order-text">
              {activity.items[itemIndex]}
            </span>
            <span className="activity-order-actions">
              <button
                type="button"
                onClick={() => move(position, -1)}
                disabled={position === 0}
                aria-label={`Mover “${activity.items[itemIndex]}” para cima`}
              >
                ↑
              </button>
              <button
                type="button"
                onClick={() => move(position, 1)}
                disabled={position === order.length - 1}
                aria-label={`Mover “${activity.items[itemIndex]}” para baixo`}
              >
                ↓
              </button>
            </span>
          </li>
        ))}
      </ol>
      <div className="activity-form">
        <button type="button" className="activity-check" onClick={check}>
          Conferir
        </button>
        <button
          type="button"
          className="activity-reset"
          onClick={() => {
            setOrder(initial);
            setResult(null);
          }}
        >
          <RotateCcw size={13} aria-hidden="true" /> Recomeçar
        </button>
      </div>
      {result && <Feedback result={result} />}
    </div>
  );
}

function MatchingActivity({ activity, onResult }: Props) {
  if (activity.kind !== "matching") return null;
  const pairs = activity.pairs;
  const rights = useMemo(
    () =>
      shuffleStable(
        pairs.map((_, index) => index),
        activity.id + "-right"
      ),
    [activity.id, pairs]
  );
  const [selectedLeft, setSelectedLeft] = useState<number | null>(null);
  const [assignment, setAssignment] = useState<Record<number, number>>({});
  const [result, setResult] = useState<ActivityResult | null>(null);

  const pickRight = (rightIndex: number) => {
    if (selectedLeft === null) return;
    const next = { ...assignment, [selectedLeft]: rightIndex };
    setAssignment(next);
    setSelectedLeft(null);
    setResult(null);
    if (Object.keys(next).length === pairs.length) {
      const evaluated = resultFor(activity, isMatchingCorrect(activity, next));
      setResult(evaluated);
      onResult?.(evaluated);
    }
  };

  return (
    <div>
      <div className="activity-matching">
        <ul className="activity-match-column">
          {pairs.map((pair, index) => (
            <li key={pair.left}>
              <button
                type="button"
                className="activity-match-left"
                aria-pressed={selectedLeft === index}
                data-linked={assignment[index] !== undefined}
                onClick={() => setSelectedLeft(index)}
              >
                {pair.left}
                {assignment[index] !== undefined && (
                  <span className="activity-match-link" aria-hidden="true">
                    → {pairs[assignment[index]].right}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
        <ul className="activity-match-column">
          {rights.map(rightIndex => (
            <li key={pairs[rightIndex].right}>
              <button
                type="button"
                className="activity-match-right"
                disabled={selectedLeft === null}
                onClick={() => pickRight(rightIndex)}
              >
                {pairs[rightIndex].right}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <p className="activity-hint">
        {selectedLeft === null
          ? "Primeiro escolha um item da coluna da esquerda."
          : `Agora escolha o par de “${pairs[selectedLeft].left}”.`}
      </p>
      <div className="activity-form">
        <button
          type="button"
          className="activity-reset"
          onClick={() => {
            setAssignment({});
            setSelectedLeft(null);
            setResult(null);
          }}
        >
          <RotateCcw size={13} aria-hidden="true" /> Recomeçar
        </button>
      </div>
      {result && <Feedback result={result} />}
    </div>
  );
}
