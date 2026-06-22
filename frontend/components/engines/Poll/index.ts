import type { PollData } from "@/types/engines";
import type { EngineModule } from "../types";
import { PollBuilder } from "./Builder";
import { PollPlay } from "./Play";

export const PollEngine: EngineModule<PollData> = {
  slug: "poll",
  name: "So'rovnoma",
  empty: () => ({ question: "", options: ["", ""] }),
  isValid: (d) =>
    d.question.trim().length > 0 &&
    d.options.length >= 2 &&
    d.options.every((o) => o.trim().length > 0),
  Play: PollPlay,
  Builder: PollBuilder,
};
