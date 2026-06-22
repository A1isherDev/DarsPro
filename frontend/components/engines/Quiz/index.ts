import type { QuizData } from "@/types/engines";
import type { EngineModule } from "../types";
import { QuizBuilder } from "./Builder";
import { QuizPlay } from "./Play";

export const QuizEngine: EngineModule<QuizData> = {
  slug: "quiz",
  name: "Quiz",
  empty: () => ({
    questions: [
      { text: "", image: null, options: ["", ""], answer: 0, time_limit: 30 },
    ],
  }),
  isValid: (d) =>
    d.questions.length > 0 &&
    d.questions.every(
      (q) =>
        q.text.trim().length > 0 &&
        q.options.length >= 2 &&
        q.options.every((o) => o.trim().length > 0)
    ),
  Play: QuizPlay,
  Builder: QuizBuilder,
};
