"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { TrueFalseData } from "@/types/engines";
import type { BuilderProps } from "../types";

export function TrueFalseBuilder({ value, onChange }: BuilderProps<TrueFalseData>) {
  const statements = value.statements ?? [];

  function update(i: number, patch: Partial<{ text: string; answer: boolean }>) {
    onChange({
      statements: statements.map((s, j) => (j === i ? { ...s, ...patch } : s)),
    });
  }

  return (
    <div className="space-y-3">
      {statements.map((s, i) => (
        <Card key={i}>
          <CardContent className="space-y-2 pt-5">
            <div className="flex items-center justify-between">
              <Label>Bayonot {i + 1}</Label>
              <Button
                variant="ghost"
                size="icon"
                onClick={() =>
                  onChange({ statements: statements.filter((_, j) => j !== i) })
                }
              >
                <Trash2 size={16} className="text-destructive" />
              </Button>
            </div>
            <Input
              placeholder="Bayonot matni"
              value={s.text}
              onChange={(e) => update(i, { text: e.target.value })}
            />
            <div className="flex gap-2">
              {[true, false].map((val) => (
                <button
                  key={String(val)}
                  onClick={() => update(i, { answer: val })}
                  className={cn(
                    "rounded-lg px-4 py-1.5 text-sm font-semibold transition-colors",
                    s.answer === val
                      ? val
                        ? "bg-success text-white"
                        : "bg-destructive text-white"
                      : "bg-muted text-muted-foreground"
                  )}
                >
                  {val ? "To'g'ri" : "Noto'g'ri"}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
      <Button
        variant="outline"
        onClick={() =>
          onChange({ statements: [...statements, { text: "", answer: true }] })
        }
      >
        + Bayonot qo'shish
      </Button>
    </div>
  );
}
