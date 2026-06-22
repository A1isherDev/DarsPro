"use client";

import { useMemo, useState } from "react";

import { motion } from "framer-motion";

import { Celebrate } from "@/components/ui/celebrate";
import { cn } from "@/lib/utils";
import type { EngineDataMap } from "@/types/engines";
import type { PlayProps } from "../types";

type MemoryData = EngineDataMap["memory"];

interface Tile {
  key: string;
  pairId: number;
  text: string;
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function MemoryPlay({ data, onFinish }: PlayProps<MemoryData>) {
  const pairs = data.pairs ?? [];
  const tiles = useMemo<Tile[]>(
    () =>
      shuffle(
        pairs.flatMap((p, i) => [
          { key: `${i}a`, pairId: i, text: p.a },
          { key: `${i}b`, pairId: i, text: p.b },
        ])
      ),
    [pairs]
  );

  const [flipped, setFlipped] = useState<string[]>([]);
  const [matched, setMatched] = useState<Set<number>>(new Set());
  const [score, setScore] = useState(0);
  const [busy, setBusy] = useState(false);

  if (pairs.length === 0) {
    return <p className="text-muted-foreground">Juftliklar yo'q.</p>;
  }

  function flip(tile: Tile) {
    if (busy || matched.has(tile.pairId) || flipped.includes(tile.key)) return;
    const next = [...flipped, tile.key];
    setFlipped(next);
    if (next.length === 2) {
      setBusy(true);
      const [a, b] = next.map((k) => tiles.find((t) => t.key === k)!);
      if (a.pairId === b.pairId) {
        const m = new Set(matched).add(a.pairId);
        setMatched(m);
        setScore((s) => s + 100);
        setFlipped([]);
        setBusy(false);
        if (m.size === pairs.length) onFinish?.(score + 100);
      } else {
        setTimeout(() => {
          setFlipped([]);
          setBusy(false);
        }, 800);
      }
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
        <Celebrate title="Ajoyib!" subtitle={`Barcha juftliklar ochildi. Ball: ${score}`} />
      ) : (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
          {tiles.map((t) => {
            const isMatched = matched.has(t.pairId);
            const open = flipped.includes(t.key) || isMatched;
            return (
              <motion.button
                key={t.key}
                onClick={() => flip(t)}
                whileTap={{ scale: 0.95 }}
                animate={isMatched ? { scale: [1, 1.08, 1] } : {}}
                className={cn(
                  "flex h-20 items-center justify-center rounded-xl border p-2 text-center text-sm font-semibold transition-colors [transform-style:preserve-3d]",
                  open
                    ? isMatched
                      ? "border-success bg-success/10 text-success"
                      : "border-primary bg-primary/10"
                    : "border-border bg-muted hover:bg-muted/70"
                )}
              >
                {open ? t.text : "?"}
              </motion.button>
            );
          })}
        </div>
      )}
    </div>
  );
}
