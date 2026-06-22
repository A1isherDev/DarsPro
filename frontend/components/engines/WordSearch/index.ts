import type { EngineDataMap } from "@/types/engines";
import type { EngineModule } from "../types";
import { WordSearchBuilder } from "./Builder";
import { WordSearchPlay } from "./Play";

type WSData = EngineDataMap["word_search"];

export const WordSearchEngine: EngineModule<WSData> = {
  slug: "word_search",
  name: "So'z izlash",
  empty: () => ({ words: [""], grid_size: 10 }),
  isValid: (d) =>
    d.words.length > 0 &&
    d.words.every(
      (w) => w.trim().length > 0 && w.trim().length <= d.grid_size
    ),
  Play: WordSearchPlay,
  Builder: WordSearchBuilder,
};
