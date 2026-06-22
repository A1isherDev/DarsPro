"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

import { Card, CardContent } from "@/components/ui/card";
import { Celebrate } from "@/components/ui/celebrate";
import { cn } from "@/lib/utils";
import type { TrueFalseData } from "@/types/engines";
import type { PlayProps } from "../types";

export function TrueFalsePlay({ data, onFinish }: PlayProps<TrueFalseData>) {
  const statements = data.statements ?? [];
  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [picked, setPicked] = useState<boolean | null>(null);
  const [finished, setFinished] = useState(false);

  if (statements.length === 0) {
    return <p className="text-muted-foreground">Bayonotlar yo'q.</p>;
  }

  const s = statements[index];

  function choose(val: boolean) {
    if (picked !== null) return;
    setPicked(val);
    if (val === s.answer) setScore((x) => x + 100);
  }

  function next() {
    if (index + 1 >= statements.length) {
      setFinished(true);
      onFinish?.(score);
    } else {
      setIndex((i) => i + 1);
      setPicked(null);
    }
  }

  if (finished) {
    return <Celebrate title="O'yin tugadi!" subtitle={`Ball: ${score}`} />;
  }

  return (
    <div className="space-y-4">
      <p className="text-sm font-semibold text-muted-foreground">
        {index + 1} / {statements.length} · {score} ball
      </p>
      <AnimatePresence mode="wait">
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
        >
          <Card>
            <CardContent className="pt-6 text-center">
              <p className="mb-5 font-display text-xl font-bold">{s.text}</p>
              <div className="flex justify-center gap-3">
                {[true, false].map((val) => {
                  const reveal = picked !== null;
                  const correct = val === s.answer;
                  const isPicked = picked === val;
                  return (
                    <motion.button
                      key={String(val)}
                      whileTap={{ scale: 0.95 }}
                      animate={reveal && isPicked && !correct ? { x: [0, -6, 6, 0] } : {}}
                      onClick={() => choose(val)}
                      disabled={reveal}
                      className={cn(
                        "min-w-28 rounded-xl px-6 py-4 font-display text-lg font-bold text-white shadow-soft",
                        val ? "bg-success" : "bg-destructive",
                        reveal && !correct && !isPicked && "opacity-40",
                        reveal && correct && "ring-4 ring-foreground/20"
                      )}
                    >
                      {val ? "To'g'ri" : "Noto'g'ri"}
                    </motion.button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>
      {picked !== null && (
        <div className="flex justify-end">
          <button
            onClick={next}
            className="rounded-lg bg-primary px-4 py-2 font-semibold text-primary-foreground"
          >
            {index + 1 >= statements.length ? "Yakunlash" : "Keyingisi"}
          </button>
        </div>
      )}
    </div>
  );
}
