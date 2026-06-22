"use client";

import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Celebrate } from "@/components/ui/celebrate";
import { cn } from "@/lib/utils";
import type { EngineDataMap } from "@/types/engines";
import type { PlayProps } from "../types";

type SortData = EngineDataMap["sort_order"];

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function SortOrderPlay({ data, onFinish }: PlayProps<SortData>) {
  const correct = useMemo(
    () => [...(data.items ?? [])].sort((a, b) => a.order - b.order),
    [data.items]
  );
  const [order, setOrder] = useState<string[]>(() =>
    shuffle(correct.map((i) => i.text))
  );
  const [checked, setChecked] = useState(false);

  if (correct.length < 2) {
    return <p className="text-muted-foreground">Kamida 2 ta element kerak.</p>;
  }

  function move(i: number, dir: -1 | 1) {
    const j = i + dir;
    if (j < 0 || j >= order.length) return;
    const next = [...order];
    [next[i], next[j]] = [next[j], next[i]];
    setOrder(next);
    setChecked(false);
  }

  const correctText = correct.map((c) => c.text);
  const allRight = checked && order.every((t, i) => t === correctText[i]);

  function check() {
    setChecked(true);
    if (order.every((t, i) => t === correctText[i])) {
      onFinish?.(order.length * 100);
    }
  }

  return (
    <div className="space-y-4">
      {data.title && <h2 className="font-display text-lg font-semibold">{data.title}</h2>}
      <div className="space-y-2">
        {order.map((text, i) => {
          const right = checked && text === correctText[i];
          const wrong = checked && text !== correctText[i];
          return (
            <motion.div
              layout
              key={text}
              transition={{ type: "spring", stiffness: 500, damping: 35 }}
            >
            <Card
              className={cn(
                right && "border-success bg-success/10",
                wrong && "border-destructive bg-destructive/10"
              )}
            >
              <CardContent className="flex items-center justify-between gap-2 py-3">
                <span className="text-sm font-medium">
                  {i + 1}. {text}
                </span>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => move(i, -1)}
                    disabled={i === 0}
                  >
                    <ChevronUp size={16} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => move(i, 1)}
                    disabled={i === order.length - 1}
                  >
                    <ChevronDown size={16} />
                  </Button>
                </div>
              </CardContent>
            </Card>
            </motion.div>
          );
        })}
      </div>

      {allRight ? (
        <Celebrate emoji="✅" title="To'g'ri tartib!" />
      ) : (
        <div className="flex justify-end">
          <Button onClick={check}>Tekshirish</Button>
        </div>
      )}
    </div>
  );
}
