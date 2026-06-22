import type { MatchingData } from "@/types/engines";
import type { EngineModule } from "../types";
import { MatchingBuilder } from "./Builder";
import { MatchingPlay } from "./Play";

export const MatchingEngine: EngineModule<MatchingData> = {
  slug: "matching",
  name: "Matching",
  empty: () => ({ pairs: [{ term: "", definition: "" }] }),
  isValid: (d) =>
    d.pairs.length > 0 &&
    d.pairs.every(
      (p) => p.term.trim().length > 0 && p.definition.trim().length > 0
    ),
  Play: MatchingPlay,
  Builder: MatchingBuilder,
};
