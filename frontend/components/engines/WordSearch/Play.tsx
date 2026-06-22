"use client";

import { useMemo, useState } from "react";

import { Card, CardContent } from "@/components/ui/card";
import { Celebrate } from "@/components/ui/celebrate";
import { cn } from "@/lib/utils";
import type { EngineDataMap } from "@/types/engines";
import type { PlayProps } from "../types";

type WSData = EngineDataMap["word_search"];

const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const DIRS = [
  [0, 1],
  [1, 0],
  [1, 1],
  [-1, 1],
];

function buildGrid(rawWords: string[], size: number) {
  const words = rawWords
    .map((w) => w.trim().toUpperCase())
    .filter((w) => w.length > 0 && w.length <= size);
  const grid: (string | null)[][] = Array.from({ length: size }, () =>
    Array<string | null>(size).fill(null)
  );
  const placed: string[] = [];

  for (const word of words) {
    let done = false;
    for (let attempt = 0; attempt < 100 && !done; attempt++) {
      const [dr, dc] = DIRS[Math.floor(Math.random() * DIRS.length)];
      const r0 = Math.floor(Math.random() * size);
      const c0 = Math.floor(Math.random() * size);
      const rEnd = r0 + dr * (word.length - 1);
      const cEnd = c0 + dc * (word.length - 1);
      if (rEnd < 0 || rEnd >= size || cEnd < 0 || cEnd >= size) continue;
      let ok = true;
      for (let k = 0; k < word.length; k++) {
        const cell = grid[r0 + dr * k][c0 + dc * k];
        if (cell !== null && cell !== word[k]) {
          ok = false;
          break;
        }
      }
      if (!ok) continue;
      for (let k = 0; k < word.length; k++) {
        grid[r0 + dr * k][c0 + dc * k] = word[k];
      }
      placed.push(word);
      done = true;
    }
  }

  const filled = grid.map((row) =>
    row.map((c) => c ?? ALPHABET[Math.floor(Math.random() * ALPHABET.length)])
  );
  return { grid: filled, placed };
}

function lineCells(
  r0: number,
  c0: number,
  r1: number,
  c1: number
): [number, number][] | null {
  const dr = Math.sign(r1 - r0);
  const dc = Math.sign(c1 - c0);
  const lenR = Math.abs(r1 - r0);
  const lenC = Math.abs(c1 - c0);
  // To'g'ri chiziq: gorizontal, vertikal yoki diagonal
  if (!(lenR === 0 || lenC === 0 || lenR === lenC)) return null;
  const steps = Math.max(lenR, lenC);
  const cells: [number, number][] = [];
  for (let k = 0; k <= steps; k++) cells.push([r0 + dr * k, c0 + dc * k]);
  return cells;
}

export function WordSearchPlay({ data, onFinish }: PlayProps<WSData>) {
  const size = data.grid_size ?? 10;
  const { grid, placed } = useMemo(
    () => buildGrid(data.words ?? [], size),
    [data.words, size]
  );

  const [start, setStart] = useState<[number, number] | null>(null);
  const [found, setFound] = useState<Set<string>>(new Set());
  const [foundCells, setFoundCells] = useState<Set<string>>(new Set());

  if (!data.words || data.words.length === 0) {
    return <p className="text-muted-foreground">So'zlar yo'q.</p>;
  }

  function clickCell(r: number, c: number) {
    if (!start) {
      setStart([r, c]);
      return;
    }
    const cells = lineCells(start[0], start[1], r, c);
    setStart(null);
    if (!cells) return;
    const str = cells.map(([cr, cc]) => grid[cr][cc]).join("");
    const rev = str.split("").reverse().join("");
    const match = placed.find(
      (w) => !found.has(w) && (w === str || w === rev)
    );
    if (match) {
      const nf = new Set(found).add(match);
      setFound(nf);
      const fc = new Set(foundCells);
      cells.forEach(([cr, cc]) => fc.add(`${cr},${cc}`));
      setFoundCells(fc);
      if (nf.size === placed.length) onFinish?.(placed.length * 100);
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        So'z boshi va oxiri katakchasini bosing. Topilgan: {found.size} /{" "}
        {placed.length}
      </p>

      <div className="overflow-x-auto">
        <div
          className="grid gap-0.5"
          style={{ gridTemplateColumns: `repeat(${size}, minmax(0, 1fr))`, maxWidth: size * 40 }}
        >
          {grid.map((row, r) =>
            row.map((ch, c) => {
              const key = `${r},${c}`;
              const isFound = foundCells.has(key);
              const isStart = start && start[0] === r && start[1] === c;
              return (
                <button
                  key={key}
                  onClick={() => clickCell(r, c)}
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-lg text-sm font-semibold uppercase transition-colors",
                    isFound
                      ? "bg-success/30 text-success"
                      : isStart
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted hover:bg-muted/60"
                  )}
                >
                  {ch}
                </button>
              );
            })
          )}
        </div>
      </div>

      <Card>
        <CardContent className="flex flex-wrap gap-2 pt-4">
          {placed.map((w) => (
            <span
              key={w}
              className={cn(
                "rounded-full border border-border px-3 py-1 text-sm",
                found.has(w) && "text-muted-foreground line-through"
              )}
            >
              {w}
            </span>
          ))}
        </CardContent>
      </Card>

      {found.size === placed.length && (
        <Celebrate title="Barcha so'zlar topildi!" />
      )}
    </div>
  );
}
