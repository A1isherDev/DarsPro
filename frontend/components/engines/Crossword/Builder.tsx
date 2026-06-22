"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import type { EngineDataMap } from "@/types/engines";
import type { BuilderProps } from "../types";

type CrosswordData = EngineDataMap["crossword"];

export function CrosswordBuilder({ value, onChange }: BuilderProps<CrosswordData>) {
  const words = value.words ?? [];

  function update(i: number, patch: Partial<{ word: string; clue: string }>) {
    onChange({ words: words.map((w, j) => (j === i ? { ...w, ...patch } : w)) });
  }

  return (
    <div className="space-y-3">
      {words.map((w, i) => (
        <Card key={i}>
          <CardContent className="pt-5">
            <div className="flex items-center justify-between">
              <Label>So'z {i + 1}</Label>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onChange({ words: words.filter((_, j) => j !== i) })}
              >
                <Trash2 size={16} className="text-destructive" />
              </Button>
            </div>
            <div className="mt-2 space-y-2">
              <Input
                placeholder="So'z (masalan: ATOM)"
                value={w.word}
                onChange={(e) => update(i, { word: e.target.value })}
              />
              <Input
                placeholder="Ishora / ta'rif"
                value={w.clue}
                onChange={(e) => update(i, { clue: e.target.value })}
              />
            </div>
          </CardContent>
        </Card>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange({ words: [...words, { word: "", clue: "" }] })}
      >
        + So'z qo'shish
      </Button>
    </div>
  );
}
