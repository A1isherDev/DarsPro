"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Celebrate } from "@/components/ui/celebrate";
import { cn } from "@/lib/utils";
import type { EngineDataMap } from "@/types/engines";
import type { PlayProps } from "../types";

type CrosswordData = EngineDataMap["crossword"];

export function CrosswordPlay({ data, onFinish }: PlayProps<CrosswordData>) {
  const words = data.words ?? [];
  const [entries, setEntries] = useState<string[]>(() =>
    words.map(() => "")
  );
  const [checked, setChecked] = useState(false);

  if (words.length === 0) {
    return <p className="text-muted-foreground">So'zlar yo'q.</p>;
  }

  function norm(s: string) {
    return s.trim().toLocaleUpperCase("uz");
  }

  function isRight(i: number) {
    return norm(entries[i]) === norm(words[i].word);
  }

  function check() {
    setChecked(true);
    if (words.every((_, i) => isRight(i))) onFinish?.(words.length * 100);
  }

  const allRight = checked && words.every((_, i) => isRight(i));

  return (
    <div className="space-y-4">
      {words.map((w, i) => {
        const letters = w.word.split("");
        const value = entries[i];
        return (
          <Card key={i}>
            <CardContent className="space-y-2 pt-4">
              <p className="text-sm">
                <span className="font-semibold">{i + 1}.</span> {w.clue}
              </p>
              <div className="flex flex-wrap gap-1">
                {letters.map((_, li) => (
                  <span
                    key={li}
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-lg border border-border text-base font-bold uppercase",
                      checked &&
                        (isRight(i)
                          ? "border-success bg-success/10"
                          : "border-destructive bg-destructive/10")
                    )}
                  >
                    {value[li] ?? ""}
                  </span>
                ))}
              </div>
              <input
                value={value}
                maxLength={letters.length}
                onChange={(e) => {
                  const next = [...entries];
                  next[i] = e.target.value;
                  setEntries(next);
                  setChecked(false);
                }}
                className="w-full rounded-md border border-border bg-muted px-3 py-1.5 text-sm uppercase tracking-widest focus:outline-none focus:border-primary"
                placeholder="Javobni yozing"
              />
            </CardContent>
          </Card>
        );
      })}

      {allRight ? (
        <Celebrate title="Hammasi to'g'ri!" />
      ) : (
        <div className="flex justify-end">
          <Button onClick={check}>Tekshirish</Button>
        </div>
      )}
    </div>
  );
}
