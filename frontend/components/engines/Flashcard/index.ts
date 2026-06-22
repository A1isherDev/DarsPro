import type { FlashcardData } from "@/types/engines";
import type { EngineModule } from "../types";
import { FlashcardBuilder } from "./Builder";
import { FlashcardPlay } from "./Play";

export const FlashcardEngine: EngineModule<FlashcardData> = {
  slug: "flashcard",
  name: "Flashcard",
  empty: () => ({ cards: [{ front: "", back: "" }] }),
  isValid: (d) =>
    d.cards.length > 0 &&
    d.cards.every((c) => c.front.trim().length > 0 && c.back.trim().length > 0),
  Play: FlashcardPlay,
  Builder: FlashcardBuilder,
};
