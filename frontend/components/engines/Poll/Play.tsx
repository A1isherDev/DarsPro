"use client";

import { motion } from "framer-motion";
import { useState } from "react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { PollData } from "@/types/engines";
import type { PlayProps } from "../types";

export function PollPlay({ data, onFinish }: PlayProps<PollData>) {
  const options = data.options ?? [];
  const [picked, setPicked] = useState<number | null>(null);

  if (!data.question || options.length < 2) {
    return <p className="text-muted-foreground">So'rovnoma to'liq emas.</p>;
  }

  function vote(i: number) {
    if (picked !== null) return;
    setPicked(i);
    onFinish?.(0); // so'rovnomada ball yo'q
  }

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        <h2 className="font-display text-xl font-bold">{data.question}</h2>
        <div className="space-y-2">
          {options.map((opt, i) => (
            <motion.button
              key={i}
              whileTap={{ scale: 0.97 }}
              onClick={() => vote(i)}
              disabled={picked !== null}
              className={cn(
                "flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left font-medium transition-colors",
                picked === i
                  ? "border-primary bg-primary/10"
                  : "border-border hover:bg-muted",
                picked !== null && picked !== i && "opacity-60"
              )}
            >
              <span>{opt}</span>
              {picked === i && <span className="text-primary">✓ Ovoz berildi</span>}
            </motion.button>
          ))}
        </div>
        {picked !== null && (
          <p className="text-center text-sm text-muted-foreground">
            Ovozingiz qabul qilindi. Rahmat!
          </p>
        )}
      </CardContent>
    </Card>
  );
}
