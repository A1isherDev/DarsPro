"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { EngineDataMap } from "@/types/engines";
import type { BuilderProps } from "../types";

type WSData = EngineDataMap["word_search"];

const SIZES = [8, 10, 12, 15];

export function WordSearchBuilder({ value, onChange }: BuilderProps<WSData>) {
  const words = value.words ?? [];
  const size = value.grid_size ?? 10;

  function setWord(i: number, w: string) {
    onChange({ ...value, words: words.map((x, j) => (j === i ? w : x)) });
  }

  const tooLong = words.find((w) => w.trim().length > size);

  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        <Label>Grid o'lchami</Label>
        <Select
          value={size}
          onChange={(e) =>
            onChange({ ...value, grid_size: Number(e.target.value) })
          }
          className="w-32"
        >
          {SIZES.map((s) => (
            <option key={s} value={s}>
              {s} × {s}
            </option>
          ))}
        </Select>
      </div>

      <Label>So'zlar</Label>
      {words.map((w, i) => (
        <div key={i} className="flex items-center gap-2">
          <Input
            placeholder={`So'z ${i + 1}`}
            value={w}
            onChange={(e) => setWord(i, e.target.value)}
          />
          <Button
            variant="ghost"
            size="icon"
            onClick={() =>
              onChange({ ...value, words: words.filter((_, j) => j !== i) })
            }
          >
            <Trash2 size={16} className="text-destructive" />
          </Button>
        </div>
      ))}
      {tooLong && (
        <p className="text-sm text-destructive">
          "{tooLong}" grid o'lchamidan ({size}) uzun.
        </p>
      )}
      <Button
        variant="outline"
        onClick={() => onChange({ ...value, words: [...words, ""] })}
      >
        + So'z qo'shish
      </Button>
    </div>
  );
}
