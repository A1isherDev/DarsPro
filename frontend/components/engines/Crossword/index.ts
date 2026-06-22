import type { EngineDataMap } from "@/types/engines";
import type { EngineModule } from "../types";
import { CrosswordBuilder } from "./Builder";
import { CrosswordPlay } from "./Play";

type CrosswordData = EngineDataMap["crossword"];

export const CrosswordEngine: EngineModule<CrosswordData> = {
  slug: "crossword",
  name: "Krossvord",
  empty: () => ({ words: [{ word: "", clue: "" }] }),
  isValid: (d) =>
    d.words.length > 0 &&
    d.words.every((w) => w.word.trim().length > 0 && w.clue.trim().length > 0),
  Play: CrosswordPlay,
  Builder: CrosswordBuilder,
};
