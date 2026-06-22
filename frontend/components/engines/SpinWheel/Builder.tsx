"use client";

import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { EngineDataMap } from "@/types/engines";
import type { BuilderProps } from "../types";

type SpinData = EngineDataMap["spin_wheel"];

export function SpinWheelBuilder({ value, onChange }: BuilderProps<SpinData>) {
  const items = value.items ?? [];

  function setItem(i: number, text: string) {
    onChange({ ...value, items: items.map((it, j) => (j === i ? text : it)) });
  }

  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        <Label>Tur</Label>
        <Select
          value={value.type ?? "students"}
          onChange={(e) => onChange({ ...value, type: e.target.value })}
        >
          <option value="students">O'quvchilar</option>
          <option value="topics">Mavzular</option>
          <option value="custom">Boshqa</option>
        </Select>
      </div>

      <Label>Elementlar</Label>
      {items.map((it, i) => (
        <div key={i} className="flex items-center gap-2">
          <Input
            placeholder={`Element ${i + 1}`}
            value={it}
            onChange={(e) => setItem(i, e.target.value)}
          />
          <Button
            variant="ghost"
            size="icon"
            onClick={() =>
              onChange({ ...value, items: items.filter((_, j) => j !== i) })
            }
          >
            <Trash2 size={16} className="text-destructive" />
          </Button>
        </div>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange({ ...value, items: [...items, ""] })}
      >
        + Element qo'shish
      </Button>
    </div>
  );
}
