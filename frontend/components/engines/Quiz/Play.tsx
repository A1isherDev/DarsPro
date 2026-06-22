"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { playSound } from "@/lib/sound";
import { cn } from "@/lib/utils";
import type { QuizData } from "@/types/engines";
import type { PlayProps } from "../types";

// Kahoot uslubidagi 4 rang + shakl
const TILE = [
  { bg: "bg-answer-1", shape: "▲" },
  { bg: "bg-answer-2", shape: "◆" },
  { bg: "bg-answer-3", shape: "●" },
  { bg: "bg-answer-4", shape: "■" },
];

export function QuizPlay({ data, onFinish }: PlayProps<QuizData>) {
  const questions = data.questions ?? [];
  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [finished, setFinished] = useState(false);

  const q = questions[index];
  const limit = q?.time_limit ?? 30;
  const [remaining, setRemaining] = useState(limit);

  useEffect(() => {
    setRemaining(limit);
    setPicked(null);
  }, [index, limit]);

  useEffect(() => {
    if (picked !== null || finished) return;
    if (remaining <= 0) {
      setPicked(-1);
      return;
    }
    const t = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(t);
  }, [remaining, picked, finished]);

  const total = questions.length;
  const progress = useMemo(
    () => Math.round((index / Math.max(total, 1)) * 100),
    [index, total]
  );

  if (total === 0) {
    return <p className="text-muted-foreground">Bu o'yinda savollar yo'q.</p>;
  }

  function choose(i: number) {
    if (picked !== null) return;
    setPicked(i);
    if (i === q.answer) {
      const bonus = Math.round(500 + (remaining / limit) * 500);
      setScore((s) => s + bonus);
      playSound("correct");
    } else {
      playSound("wrong");
    }
  }

  function next() {
    if (index + 1 >= total) {
      setFinished(true);
      playSound("win");
      onFinish?.(score);
    } else {
      setIndex((i) => i + 1);
    }
  }

  if (finished) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <Card className="overflow-hidden">
          <CardContent className="space-y-3 pt-8 pb-8 text-center">
            <motion.div
              className="text-6xl"
              initial={{ scale: 0 }}
              animate={{ scale: 1, rotate: [0, -10, 10, 0] }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              🎉
            </motion.div>
            <h2 className="font-display text-2xl font-bold">O'yin tugadi!</h2>
            <p className="text-lg">
              Sizning ballingiz:{" "}
              <span className="font-display font-bold text-primary">{score}</span>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span className="font-semibold">
          Savol {index + 1} / {total}
        </span>
        <motion.span
          key={remaining}
          initial={{ scale: 1.3 }}
          animate={{ scale: 1 }}
          className={cn(
            "rounded-full px-2.5 py-0.5 font-bold tabular-nums",
            remaining <= 5
              ? "bg-destructive/15 text-destructive"
              : "bg-muted text-foreground"
          )}
        >
          ⏱ {remaining}s
        </motion.span>
      </div>
      <Progress value={progress} />

      <AnimatePresence mode="wait">
        <motion.div
          key={index}
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -30 }}
        >
          <Card>
            <CardContent className="pt-6">
              {q.image && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={q.image}
                  alt=""
                  className="mb-4 max-h-56 w-full rounded-xl object-contain"
                />
              )}
              <h2 className="mb-5 font-display text-xl font-bold">{q.text}</h2>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {q.options.map((opt, i) => {
                  const tile = TILE[i % TILE.length];
                  const isAnswer = i === q.answer;
                  const isPicked = i === picked;
                  const reveal = picked !== null;
                  return (
                    <motion.button
                      key={i}
                      onClick={() => choose(i)}
                      disabled={reveal}
                      whileTap={{ scale: 0.96 }}
                      animate={
                        reveal && isPicked && !isAnswer
                          ? { x: [0, -6, 6, -6, 6, 0] }
                          : {}
                      }
                      className={cn(
                        "flex items-center gap-3 rounded-xl px-4 py-4 text-left font-semibold text-white shadow-soft transition-opacity",
                        tile.bg,
                        reveal && !isAnswer && !isPicked && "opacity-40",
                        reveal && isAnswer && "ring-4 ring-success ring-offset-2 ring-offset-background"
                      )}
                    >
                      <span className="text-lg opacity-90">{tile.shape}</span>
                      <span className="flex-1">{opt}</span>
                      {reveal && isAnswer && <span>✓</span>}
                    </motion.button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>

      {picked !== null && (
        <motion.div
          className="flex justify-end"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Button size="lg" onClick={next}>
            {index + 1 >= total ? "Yakunlash" : "Keyingi savol"}
          </Button>
        </motion.div>
      )}
    </div>
  );
}
