"use client";

import { motion } from "framer-motion";
import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import type { QuizData, QuizQuestion } from "@/types/engines";
import type { BuilderProps } from "../types";

const emptyQuestion = (): QuizQuestion => ({
  text: "",
  image: null,
  options: ["", ""],
  answer: 0,
  time_limit: 30,
});

export function QuizBuilder({ value, onChange }: BuilderProps<QuizData>) {
  const questions = value.questions ?? [];

  function update(qi: number, patch: Partial<QuizQuestion>) {
    const next = questions.map((q, i) => (i === qi ? { ...q, ...patch } : q));
    onChange({ questions: next });
  }

  function setOption(qi: number, oi: number, text: string) {
    const q = questions[qi];
    const options = q.options.map((o, i) => (i === oi ? text : o));
    update(qi, { options });
  }

  function addOption(qi: number) {
    const q = questions[qi];
    if (q.options.length >= 4) return;
    update(qi, { options: [...q.options, ""] });
  }

  function removeOption(qi: number, oi: number) {
    const q = questions[qi];
    if (q.options.length <= 2) return;
    const options = q.options.filter((_, i) => i !== oi);
    const answer = q.answer >= options.length ? 0 : q.answer;
    update(qi, { options, answer });
  }

  return (
    <div className="space-y-4">
      {questions.map((q, qi) => (
        <motion.div key={qi} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardContent className="space-y-3 pt-5">
            <div className="flex items-center justify-between">
              <Label>Savol {qi + 1}</Label>
              <Button
                variant="ghost"
                size="icon"
                onClick={() =>
                  onChange({ questions: questions.filter((_, i) => i !== qi) })
                }
              >
                <Trash2 size={16} className="text-destructive" />
              </Button>
            </div>
            <Input
              placeholder="Savol matni"
              value={q.text}
              onChange={(e) => update(qi, { text: e.target.value })}
            />
            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Variantlar (to'g'risini belgilang)
              </Label>
              {q.options.map((opt, oi) => (
                <div key={oi} className="flex items-center gap-2">
                  <input
                    type="radio"
                    name={`answer-${qi}`}
                    checked={q.answer === oi}
                    onChange={() => update(qi, { answer: oi })}
                    className="h-4 w-4"
                  />
                  <Input
                    placeholder={`Variant ${oi + 1}`}
                    value={opt}
                    onChange={(e) => setOption(qi, oi, e.target.value)}
                  />
                  {q.options.length > 2 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeOption(qi, oi)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  )}
                </div>
              ))}
              {q.options.length < 4 && (
                <Button variant="outline" size="sm" onClick={() => addOption(qi)}>
                  + Variant qo'shish
                </Button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-xs text-muted-foreground">Vaqt (s)</Label>
              <Input
                type="number"
                min={5}
                max={120}
                className="w-24"
                value={q.time_limit}
                onChange={(e) =>
                  update(qi, { time_limit: Number(e.target.value) || 30 })
                }
              />
            </div>
          </CardContent>
        </Card>
        </motion.div>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange({ questions: [...questions, emptyQuestion()] })}
      >
        + Savol qo'shish
      </Button>
    </div>
  );
}
