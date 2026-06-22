"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { getEngine } from "@/components/engines/registry";
import { fetchItem, recordSoloResult } from "@/lib/content";
import { apiError } from "@/lib/api";
import type { ContentItemDetail } from "@/types/api";

export default function SoloPlayPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [item, setItem] = useState<ContentItemDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const startedAt = useRef<number>(Date.now());

  useEffect(() => {
    fetchItem(params.id)
      .then((it) => {
        setItem(it);
        startedAt.current = Date.now();
      })
      .catch((e) => setError(apiError(e)));
  }, [params.id]);

  if (error) return <p className="text-destructive">{error}</p>;
  if (!item) return <p className="text-muted-foreground">Yuklanmoqda…</p>;

  const engine = getEngine(item.engine_slug);
  if (!engine) {
    return (
      <p className="text-muted-foreground">
        Bu engine ({item.engine_slug}) hozircha qo'llab-quvvatlanmaydi.
      </p>
    );
  }

  const Play = engine.Play;

  function handleFinish(score: number) {
    const duration = Math.round((Date.now() - startedAt.current) / 1000);
    // Natijani saqlaymiz — dashboard statistikasi shu yerdan to'ladi.
    // Xatolik bo'lsa o'yin tajribasini buzmaymiz (sukutda).
    recordSoloResult({
      content: params.id,
      score: Math.max(0, Math.round(score)),
      duration_sec: duration,
    }).catch(() => {});
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{item.title}</h1>
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          ← Orqaga
        </Button>
      </div>
      <Play data={item.data} onFinish={handleFinish} />
    </div>
  );
}
