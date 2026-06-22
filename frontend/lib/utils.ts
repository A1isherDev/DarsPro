import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const PLAN_LABELS: Record<string, string> = {
  free: "Bepul",
  start: "Start",
  pro: "Pro",
  max: "Max",
};
