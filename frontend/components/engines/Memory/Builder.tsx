"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import type { EngineDataMap } from "@/types/engines";
import type { BuilderProps } from "../types";

type MemoryData = EngineDataMap["memory"];

export function MemoryBuilder({ value, onChange }: BuilderProps<MemoryData>) {
  const pairs = value.pairs ?? [];

  function update(i: number, patch: Partial<{ a: string; b: string }>) {
    onChange({ pairs: pairs.map((p, j) => (j === i ? { ...p, ...patch } : p)) });
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        Har juftlik ikki kartochka bo'ladi (masalan 🐶 va "It").
      </p>
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
                placeholder="A tomoni"
                value={p.a}
                onChange={(e) => update(i, { a: e.target.value })}
              />
              <Input
                placeholder="B tomoni"
                value={p.b}
                onChange={(e) => update(i, { b: e.target.value })}
              />
            </div>
          </CardContent>
        </Card>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange({ pairs: [...pairs, { a: "", b: "" }] })}
      >
        + Juftlik qo'shish
      </Button>
    </div>
  );
}
