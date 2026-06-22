"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import type { FlashcardData } from "@/types/engines";
import type { BuilderProps } from "../types";

export function FlashcardBuilder({
  value,
  onChange,
}: BuilderProps<FlashcardData>) {
  const cards = value.cards ?? [];

  function update(i: number, patch: Partial<{ front: string; back: string }>) {
    onChange({ cards: cards.map((c, j) => (j === i ? { ...c, ...patch } : c)) });
  }

  return (
    <div className="space-y-3">
      {cards.map((c, i) => (
        <Card key={i}>
          <CardContent className="pt-5">
            <div className="flex items-center justify-between">
              <Label>Karta {i + 1}</Label>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onChange({ cards: cards.filter((_, j) => j !== i) })}
              >
                <Trash2 size={16} className="text-destructive" />
              </Button>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2">
              <Input
                placeholder="Old tomoni (savol)"
                value={c.front}
                onChange={(e) => update(i, { front: e.target.value })}
              />
              <Input
                placeholder="Orqa tomoni (javob)"
                value={c.back}
                onChange={(e) => update(i, { back: e.target.value })}
              />
            </div>
          </CardContent>
        </Card>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange({ cards: [...cards, { front: "", back: "" }] })}
      >
        + Karta qo'shish
      </Button>
    </div>
  );
}
