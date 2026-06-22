"use client";

import { motion } from "framer-motion";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { EngineDataMap } from "@/types/engines";
import type { PlayProps } from "../types";

type SpinData = EngineDataMap["spin_wheel"];

export function SpinWheelPlay({ data }: PlayProps<SpinData>) {
  const items = data.items ?? [];
  const [spinning, setSpinning] = useState(false);
  const [active, setActive] = useState<number | null>(null);
  const [winner, setWinner] = useState<number | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  if (items.length < 2) {
    return <p className="text-muted-foreground">Kamida 2 ta element kerak.</p>;
  }

  function spin() {
    if (spinning) return;
    setWinner(null);
    setSpinning(true);
    const target = Math.floor(Math.random() * items.length);
    let ticks = 0;
    const totalTicks = 20 + target + items.length * 2;
    timer.current = setInterval(() => {
      ticks++;
      setActive((a) => ((a ?? -1) + 1) % items.length);
      if (ticks >= totalTicks) {
        if (timer.current) clearInterval(timer.current);
        setActive(target);
        setWinner(target);
        setSpinning(false);
      }
    }, 80);
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {items.map((it, i) => (
          <motion.div
            key={i}
            animate={{ scale: winner === i ? 1.06 : active === i ? 1.03 : 1 }}
            className={cn(
              "rounded-xl border px-3 py-4 text-center text-sm font-semibold transition-colors",
              winner === i
                ? "border-success bg-success/20 text-success shadow-soft"
                : active === i
                ? "border-primary bg-primary/10"
                : "border-border"
            )}
          >
            {it}
          </motion.div>
        ))}
      </div>

      {winner !== null && (
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
        >
          <Card className="border-success/40 bg-success/5">
            <CardContent className="pt-5 text-center">
              <p className="text-sm text-muted-foreground">Tanlandi 🎉</p>
              <p className="font-display text-2xl font-bold text-success">
                {items[winner]}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      )}

      <div className="flex justify-center">
        <Button size="lg" onClick={spin} disabled={spinning}>
          {spinning ? "Aylanmoqda…" : "🎡 Aylantirish"}
        </Button>
      </div>
    </div>
  );
}
