// DarsPro — engine komponentlari uchun umumiy kontrakt
import type { EngineSlug } from "@/types/engines";

export interface PlayProps<T> {
  data: T;
  onFinish?: (score: number) => void;
}

export interface BuilderProps<T> {
  value: T;
  onChange: (data: T) => void;
}

export interface EngineModule<T> {
  slug: EngineSlug;
  name: string;
  empty: () => T;
  isValid: (data: T) => boolean;
  Play: React.ComponentType<PlayProps<T>>;
  Builder: React.ComponentType<BuilderProps<T>>;
}
