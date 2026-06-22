"use client";

import { Button } from "@/components/ui/button";

export function LoadMore({
  next,
  onLoad,
  loading,
}: {
  next: string | null;
  onLoad: () => void;
  loading?: boolean;
}) {
  if (!next) return null;
  return (
    <div className="flex justify-center pt-2">
      <Button variant="outline" onClick={onLoad} disabled={loading}>
        {loading ? "Yuklanmoqda…" : "Ko'proq yuklash"}
      </Button>
    </div>
  );
}
