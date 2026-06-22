"use client";

import { Volume2, VolumeX } from "lucide-react";
import { useEffect, useState } from "react";

import { isMuted, setMuted } from "@/lib/sound";
import { cn } from "@/lib/utils";

export function SoundToggle({ className }: { className?: string }) {
  const [muted, setM] = useState(false);

  useEffect(() => {
    setM(isMuted());
  }, []);

  function toggle() {
    const next = !muted;
    setMuted(next);
    setM(next);
  }

  return (
    <button
      onClick={toggle}
      title={muted ? "Ovozni yoqish" : "Ovozni o'chirish"}
      className={cn(
        "rounded-md p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
        className
      )}
    >
      {muted ? <VolumeX size={18} /> : <Volume2 size={18} />}
    </button>
  );
}
