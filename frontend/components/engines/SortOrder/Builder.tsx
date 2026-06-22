"use client";

import { ChevronDown, ChevronUp, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import type { EngineDataMap } from "@/types/engines";
import type { BuilderProps } from "../types";

type SortData = EngineDataMap["sort_order"];

export function SortOrderBuilder({ value, onChange }: BuilderProps<SortData>) {
  const items = value.items ?? [];

  // To'g'ri tartib = ro'yxat tartibi. order har doim pozitsiyadan hisoblanadi.
  function commit(list: { text: string; order: number }[]) {
    onChange({
      ...value,
      items: list.map((it, i) => ({ text: it.text, order: i + 1 })),
    });
  }

  function setText(i: number, text: string) {
    commit(items.map((it, j) => (j === i ? { ...it, text } : it)));
  }

  function move(i: number, dir: -1 | 1) {
    const j = i + dir;
    if (j < 0 || j >= items.length) return;
    const next = [...items];
    [next[i], next[j]] = [next[j], next[i]];
    commit(next);
  }

  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        <Label>Sarlavha</Label>
        <Input
          placeholder="Masalan: O'simlik o'sish bosqichlari"
          value={value.title ?? ""}
          onChange={(e) => onChange({ ...value, title: e.target.value })}
        />
      </div>

      <Label>Elementlar (to'g'ri tartibda)</Label>
      {items.map((it, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="w-6 text-sm text-muted-foreground">{i + 1}.</span>
          <Input
            placeholder={`Element ${i + 1}`}
            value={it.text}
            onChange={(e) => setText(i, e.target.value)}
          />
          <Button variant="ghost" size="icon" onClick={() => move(i, -1)} disabled={i === 0}>
            <ChevronUp size={16} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => move(i, 1)}
            disabled={i === items.length - 1}
          >
            <ChevronDown size={16} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => commit(items.filter((_, j) => j !== i))}
          >
            <Trash2 size={16} className="text-destructive" />
          </Button>
        </div>
      ))}
      <Button variant="outline" onClick={() => commit([...items, { text: "", order: 0 }])}>
        + Element qo'shish
      </Button>
    </div>
  );
}
