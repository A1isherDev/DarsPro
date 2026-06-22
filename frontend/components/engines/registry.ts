// DarsPro — engine registri. Slug -> engine moduli.
import type { EngineSlug } from "@/types/engines";
import type { EngineModule } from "./types";
import { CrosswordEngine } from "./Crossword";
import { FillBlankEngine } from "./FillBlank";
import { FlashcardEngine } from "./Flashcard";
import { MatchingEngine } from "./Matching";
import { MemoryEngine } from "./Memory";
import { PollEngine } from "./Poll";
import { QuizEngine } from "./Quiz";
import { SortOrderEngine } from "./SortOrder";
import { SpinWheelEngine } from "./SpinWheel";
import { TrueFalseEngine } from "./TrueFalse";
import { WordSearchEngine } from "./WordSearch";

// Data tipi modul ichida aniq; registr darajasida `unknown` bilan saqlanadi.
type AnyEngine = EngineModule<unknown>;

// Har bir modul o'z data tipiga ega; registrda tipni `unknown` ga keltiriб
// birlashtiramiz (Play/Builder data'ni o'z ichida to'g'ri talqin qiladi).
const ENGINE_LIST = [
  QuizEngine,
  MatchingEngine,
  FlashcardEngine,
  SpinWheelEngine,
  MemoryEngine,
  CrosswordEngine,
  SortOrderEngine,
  FillBlankEngine,
  WordSearchEngine,
  TrueFalseEngine,
  PollEngine,
] as unknown as AnyEngine[];

export const ENGINES: Partial<Record<EngineSlug, AnyEngine>> =
  Object.fromEntries(ENGINE_LIST.map((e) => [e.slug, e]));

export function getEngine(slug: EngineSlug): AnyEngine | null {
  return ENGINES[slug] ?? null;
}

// Builder'da tanlanadigan enginelar (registr tartibida)
export const BUILDABLE_ENGINES = Object.values(ENGINES) as AnyEngine[];
