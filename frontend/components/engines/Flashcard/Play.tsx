"use client";

import { motion } from "framer-motion";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type { FlashcardData } from "@/types/engines";
import type { PlayProps } from "../types";

export function FlashcardPlay({ data, onFinish }: PlayProps<FlashcardData>) {
  const cards = data.cards ?? [];
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  if (cards.length === 0) {
    return <p className="text-muted-foreground">Kartalar yo'q.</p>;
  }

  const card = cards[index];

  function go(delta: number) {
    const nextIdx = index + delta;
    if (nextIdx < 0 || nextIdx >= cards.length) return;
    setIndex(nextIdx);
    setFlipped(false);
    if (nextIdx === cards.length - 1) onFinish?.(cards.length);
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <p className="text-center text-sm font-semibold text-muted-foreground">
        Karta {index + 1} / {cards.length}
      </p>
      <Progress value={((index + 1) / cards.length) * 100} />

      <div
        className="relative h-60 cursor-pointer select-none [perspective:1200px]"
        onClick={() => setFlipped((f) => !f)}
      >
        <motion.div
          className="relative h-full w-full [transform-style:preserve-3d]"
          animate={{ rotateY: flipped ? 180 : 0 }}
          transition={{ duration: 0.5 }}
          key={index}
        >
          {/* Old tomon */}
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-card p-8 text-center shadow-card [backface-visibility:hidden]">
            <span className="text-xs font-semibold uppercase tracking-wide text-primary">
              Savol
            </span>
            <p className="font-display text-2xl font-bold">{card.front}</p>
            <span className="text-xs text-muted-foreground">
              (aylantirish uchun bosing)
            </span>
          </div>
          {/* Orqa tomon */}
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-2xl border border-primary/40 bg-primary/10 p-8 text-center shadow-card [backface-visibility:hidden] [transform:rotateY(180deg)]">
            <span className="text-xs font-semibold uppercase tracking-wide text-accent">
              Javob
            </span>
            <p className="font-display text-2xl font-bold">{card.back}</p>
          </div>
        </motion.div>
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={() => go(-1)} disabled={index === 0}>
          ← Oldingi
        </Button>
        <Button onClick={() => go(1)} disabled={index === cards.length - 1}>
          Keyingi →
        </Button>
      </div>
    </div>
  );
}
