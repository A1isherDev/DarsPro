"use client";

import { motion } from "framer-motion";
import { useMemo, useState } from "react";

import { Celebrate } from "@/components/ui/celebrate";
import { cn } from "@/lib/utils";
import type { MatchingData } from "@/types/engines";
import type { PlayProps } from "../types";

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function MatchingPlay({ data, onFinish }: PlayProps<MatchingData>) {
  const pairs = data.pairs ?? [];
  const defs = useMemo(
    () => shuffle(pairs.map((p, i) => ({ text: p.definition, idx: i }))),
    [pairs]
  );

  const [selectedTerm, setSelectedTerm] = useState<number | null>(null);
  const [matched, setMatched] = useState<Set<number>>(new Set());
  const [wrong, setWrong] = useState<number | null>(null);
  const [score, setScore] = useState(0);

  if (pairs.length === 0) {
    return <p className="text-muted-foreground">Juftliklar yo'q.</p>;
  }

  function pickDef(defIdx: number) {
    if (selectedTerm === null) return;
    if (defIdx === selectedTerm) {
      const next = new Set(matched).add(defIdx);
      setMatched(next);
      setScore((s) => s + 100);
      setSelectedTerm(null);
      if (next.size === pairs.length) onFinish?.(score + 100);
    } else {
      setWrong(defIdx);
      setTimeout(() => setWrong(null), 600);
    }
  }

  const done = matched.size === pairs.length;

  return (
    <div className="space-y-4">
      <div className="flex justify-between text-sm text-muted-foreground">
        <span>
          Topildi: {matched.size} / {pairs.length}
        </span>
        <span>{score} ball</span>
      </div>

      {done ? (
        <Celebrate emoji="🎯" title="Barakalla!" subtitle={`Barcha juftliklar topildi. Ball: ${score}`} />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            {pairs.map((p, i) => (
              <motion.button
                key={i}
                disabled={matched.has(i)}
                onClick={() => setSelectedTerm(i)}
                whileTap={{ scale: 0.97 }}
                animate={matched.has(i) ? { scale: [1, 1.05, 1] } : {}}
                className={cn(
                  "w-full rounded-xl border px-3 py-3 text-left text-sm font-semibold transition-colors",
                  matched.has(i)
                    ? "border-success bg-success/10 text-success opacity-70"
                    : selectedTerm === i
                    ? "border-primary bg-primary/10"
                    : "border-border hover:bg-muted"
                )}
              >
                {p.term}
              </motion.button>
            ))}
          </div>
          <div className="space-y-2">
            {defs.map(({ text, idx }) => (
              <motion.button
                key={idx}
                disabled={matched.has(idx)}
                onClick={() => pickDef(idx)}
                whileTap={{ scale: 0.97 }}
                animate={wrong === idx ? { x: [0, -6, 6, -6, 6, 0] } : {}}
                className={cn(
                  "w-full rounded-xl border px-3 py-3 text-left text-sm transition-colors",
                  matched.has(idx)
                    ? "border-success bg-success/10 text-success opacity-70"
                    : wrong === idx
                    ? "border-destructive bg-destructive/10"
                    : "border-border hover:bg-muted"
                )}
              >
                {text}
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
