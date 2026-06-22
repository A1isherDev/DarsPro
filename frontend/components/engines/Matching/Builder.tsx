"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import type { MatchingData } from "@/types/engines";
import type { BuilderProps } from "../types";

export function MatchingBuilder({ value, onChange }: BuilderProps<MatchingData>) {
  const pairs = value.pairs ?? [];

  function update(i: number, patch: Partial<{ term: string; definition: string }>) {
    onChange({ pairs: pairs.map((p, j) => (j === i ? { ...p, ...patch } : p)) });
  }

  return (
    <div className="space-y-3">
      {pairs.map((p, i) => (
        <Card key={i}>
          <CardContent className="pt-5">
            <div className="flex items-center justify-between">
              <Label>Juftlik {i + 1}</Label>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onChange({ pairs: pairs.filter((_, j) => j !== i) })}
              >
                <Trash2 size={16} className="text-destructive" />
              </Button>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2">
              <Input
                placeholder="Tushuncha"
                value={p.term}
                onChange={(e) => update(i, { term: e.target.value })}
              />
              <Input
                placeholder="Ta'rif"
                value={p.definition}
                onChange={(e) => update(i, { definition: e.target.value })}
              />
            </div>
          </CardContent>
        </Card>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange({ pairs: [...pairs, { term: "", definition: "" }] })}
      >
        + Juftlik qo'shish
      </Button>
    </div>
  );
}
