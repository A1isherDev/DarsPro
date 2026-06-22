// DarsPro — engine `data` JSONB sxemalari (CLAUDE.md "types/engines.ts" qoidasi)

export type EngineSlug =
  | "quiz"
  | "matching"
  | "flashcard"
  | "spin_wheel"
  | "memory"
  | "crossword"
  | "sort_order"
  | "fill_blank"
  | "word_search"
  | "true_false"
  | "poll";

export interface QuizQuestion {
  text: string;
  image: string | null;
  options: string[];
  answer: number; // to'g'ri variant indeksi
  time_limit: number;
}

export interface QuizData {
  questions: QuizQuestion[];
}

export interface MatchingPair {
  term: string;
  definition: string;
}

export interface MatchingData {
  pairs: MatchingPair[];
}

export interface FlashcardCard {
  front: string;
  back: string;
}

export interface FlashcardData {
  cards: FlashcardCard[];
}

export interface TrueFalseData {
  statements: { text: string; answer: boolean }[];
}

export interface PollData {
  question: string;
  options: string[];
}

// Engine slug -> data tipi xaritasi
export interface EngineDataMap {
  quiz: QuizData;
  matching: MatchingData;
  flashcard: FlashcardData;
  spin_wheel: { items: string[]; type: string };
  memory: { pairs: Array<{ a: string; b: string }> };
  crossword: { words: Array<{ word: string; clue: string }> };
  sort_order: { items: Array<{ text: string; order: number }>; title: string };
  fill_blank: { text: string; blanks: string[]; hints: string[] };
  word_search: { words: string[]; grid_size: number };
  true_false: TrueFalseData;
  poll: PollData;
}

// MVP'da to'liq qo'llab-quvvatlanadigan enginelar
export const MVP_ENGINES: EngineSlug[] = ["quiz", "matching", "flashcard"];
