import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

export function Spinner({
  className,
  size = 18,
}: {
  className?: string;
  size?: number;
}) {
  return <Loader2 className={cn("animate-spin", className)} size={size} />;
}

export function LoadingScreen({ label = "Yuklanmoqda…" }: { label?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-muted-foreground">
      <Spinner size={28} className="text-primary" />
      <p className="text-sm">{label}</p>
    </div>
  );
}
