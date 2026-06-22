"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import type { PollData } from "@/types/engines";
import type { BuilderProps } from "../types";

export function PollBuilder({ value, onChange }: BuilderProps<PollData>) {
  const options = value.options ?? [];

  function setOption(i: number, text: string) {
    onChange({ ...value, options: options.map((o, j) => (j === i ? text : o)) });
  }

  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        <Label>Savol</Label>
        <Input
          placeholder="So'rovnoma savoli"
          value={value.question ?? ""}
          onChange={(e) => onChange({ ...value, question: e.target.value })}
        />
      </div>
      <Label>Variantlar</Label>
      {options.map((o, i) => (
        <div key={i} className="flex items-center gap-2">
          <Input
            placeholder={`Variant ${i + 1}`}
            value={o}
            onChange={(e) => setOption(i, e.target.value)}
          />
          {options.length > 2 && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() =>
                onChange({ ...value, options: options.filter((_, j) => j !== i) })
              }
            >
              <Trash2 size={16} className="text-destructive" />
            </Button>
          )}
        </div>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange({ ...value, options: [...options, ""] })}
      >
        + Variant qo'shish
      </Button>
    </div>
  );
}
