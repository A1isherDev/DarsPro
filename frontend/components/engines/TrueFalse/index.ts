import type { TrueFalseData } from "@/types/engines";
import type { EngineModule } from "../types";
import { TrueFalseBuilder } from "./Builder";
import { TrueFalsePlay } from "./Play";

export const TrueFalseEngine: EngineModule<TrueFalseData> = {
  slug: "true_false",
  name: "To'g'ri / Noto'g'ri",
  empty: () => ({ statements: [{ text: "", answer: true }] }),
  isValid: (d) =>
    d.statements.length > 0 &&
    d.statements.every((s) => s.text.trim().length > 0),
  Play: TrueFalsePlay,
  Builder: TrueFalseBuilder,
};
