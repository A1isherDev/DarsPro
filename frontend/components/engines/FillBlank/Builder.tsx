"use client";

import { Input, Label, Textarea } from "@/components/ui/input";
import type { EngineDataMap } from "@/types/engines";
import type { BuilderProps } from "../types";

type FillData = EngineDataMap["fill_blank"];

export function FillBlankBuilder({ value, onChange }: BuilderProps<FillData>) {
  const blankCount = Math.max(0, (value.text ?? "").split("___").length - 1);
  const blanks = value.blanks ?? [];

  function setText(text: string) {
    const count = Math.max(0, text.split("___").length - 1);
    const next = Array.from({ length: count }, (_, i) => blanks[i] ?? "");
    onChange({ ...value, text, blanks: next });
  }

  function setBlank(i: number, v: string) {
    onChange({
      ...value,
      blanks: blanks.map((b, j) => (j === i ? v : b)),
    });
  }

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Matn</Label>
        <p className="text-xs text-muted-foreground">
          Bo'sh joy uchun <code>___</code> (uchta pastki chiziq) yozing.
        </p>
        <Textarea
          rows={3}
          placeholder="O'zbekiston poytaxti ___ shahridir."
          value={value.text ?? ""}
          onChange={(e) => setText(e.target.value)}
        />
      </div>

      {blankCount > 0 && (
        <div className="space-y-2">
          <Label>To'g'ri javoblar ({blankCount})</Label>
          {Array.from({ length: blankCount }).map((_, i) => (
            <Input
              key={i}
              placeholder={`${i + 1}-bo'sh joy javobi`}
              value={blanks[i] ?? ""}
              onChange={(e) => setBlank(i, e.target.value)}
            />
          ))}
        </div>
      )}

      <div className="space-y-1.5">
        <Label>Yordam (ixtiyoriy, vergul bilan)</Label>
        <Input
          placeholder="masalan: shahar, poytaxt"
          value={(value.hints ?? []).join(", ")}
          onChange={(e) =>
            onChange({
              ...value,
              hints: e.target.value
                .split(",")
                .map((h) => h.trim())
                .filter(Boolean),
            })
          }
        />
      </div>
    </div>
  );
}
