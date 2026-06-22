"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Celebrate } from "@/components/ui/celebrate";
import { cn } from "@/lib/utils";
import type { EngineDataMap } from "@/types/engines";
import type { PlayProps } from "../types";

type FillData = EngineDataMap["fill_blank"];

export function FillBlankPlay({ data, onFinish }: PlayProps<FillData>) {
  const segments = (data.text ?? "").split("___");
  const blankCount = Math.max(0, segments.length - 1);
  const [answers, setAnswers] = useState<string[]>(() =>
    Array(blankCount).fill("")
  );
  const [checked, setChecked] = useState(false);

  if (blankCount === 0) {
    return <p className="text-muted-foreground">Bo'sh joy (___) topilmadi.</p>;
  }

  const expected = data.blanks ?? [];

  function isRight(i: number) {
    return (
      answers[i].trim().toLocaleLowerCase("uz") ===
      (expected[i] ?? "").trim().toLocaleLowerCase("uz")
    );
  }

  function check() {
    setChecked(true);
    if (answers.every((_, i) => isRight(i))) {
      onFinish?.(blankCount * 100);
    }
  }

  const allRight = checked && answers.every((_, i) => isRight(i));

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="pt-6 text-lg leading-loose">
          {segments.map((seg, i) => (
            <span key={i}>
              {seg}
              {i < blankCount && (
                <input
                  value={answers[i]}
                  onChange={(e) => {
                    const next = [...answers];
                    next[i] = e.target.value;
                    setAnswers(next);
                    setChecked(false);
                  }}
                  className={cn(
                    "mx-1 inline-block w-32 rounded-md border-b-2 border-border bg-muted px-2 py-0.5 text-base focus:outline-none focus:border-primary",
                    checked && isRight(i) && "border-success bg-success/10",
                    checked && !isRight(i) && "border-destructive bg-destructive/10"
                  )}
                  placeholder="…"
                />
              )}
            </span>
          ))}
        </CardContent>
      </Card>

      {data.hints && data.hints.length > 0 && (
        <p className="text-sm text-muted-foreground">
          Yordam: {data.hints.join(", ")}
        </p>
      )}

      {checked && !allRight && (
        <p className="text-sm text-destructive">
          Ba'zi javoblar noto'g'ri — qayta urinib ko'ring.
        </p>
      )}
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
