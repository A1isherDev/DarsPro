import { describe, expect, it } from "vitest";

import { getEngine, BUILDABLE_ENGINES } from "@/components/engines/registry";
import type { EngineSlug } from "@/types/engines";

// Har engine uchun: bo'sh shablon (empty) hali yaroqsiz; to'g'ri namuna yaroqli.
const VALID: Record<EngineSlug, unknown> = {
  quiz: {
    questions: [
      { text: "2+2?", image: null, options: ["4", "5"], answer: 0, time_limit: 20 },
    ],
  },
  matching: { pairs: [{ term: "t", definition: "d" }] },
  flashcard: { cards: [{ front: "f", back: "b" }] },
  spin_wheel: { items: ["Ali", "Vali"], type: "students" },
  memory: { pairs: [{ a: "🐶", b: "It" }] },
  crossword: { words: [{ word: "ATOM", clue: "moddaning bo'lagi" }] },
  sort_order: {
    title: "Tartib",
    items: [
      { text: "Bir", order: 1 },
      { text: "Ikki", order: 2 },
    ],
  },
  fill_blank: { text: "Poytaxt ___ shahri.", blanks: ["Toshkent"], hints: [] },
  word_search: { words: ["ATOM", "ION"], grid_size: 10 },
  true_false: { statements: [{ text: "Yer dumaloq", answer: true }] },
  poll: { question: "Sevimli fan?", options: ["Matematika", "Biologiya"] },
};

const INVALID: Record<EngineSlug, unknown> = {
  quiz: { questions: [{ text: "", options: ["a"], answer: 0, time_limit: 20 }] },
  matching: { pairs: [{ term: "t", definition: "" }] },
  flashcard: { cards: [{ front: "", back: "b" }] },
  spin_wheel: { items: ["faqat-bitta"], type: "students" },
  memory: { pairs: [{ a: "x", b: "" }] },
  crossword: { words: [{ word: "", clue: "c" }] },
  sort_order: { title: "", items: [{ text: "", order: 1 }] },
  fill_blank: { text: "bo'sh joy yo'q", blanks: [], hints: [] },
  word_search: { words: ["JUDAUZUNSOZ"], grid_size: 5 },
  true_false: { statements: [{ text: "", answer: true }] },
  poll: { question: "Savol", options: ["bitta"] },
};

const SLUGS = Object.keys(VALID) as EngineSlug[];

describe("engine registri", () => {
  it("11 ta engine ro'yxatga olingan", () => {
    expect(BUILDABLE_ENGINES.length).toBe(11);
  });

  it.each(SLUGS)("'%s' engine mavjud va slug mos", (slug) => {
    const e = getEngine(slug);
    expect(e).not.toBeNull();
    expect(e!.slug).toBe(slug);
  });
});

describe("engine.isValid", () => {
  it.each(SLUGS)("'%s': bo'sh shablon yaroqsiz", (slug) => {
    const e = getEngine(slug)!;
    expect(e.isValid(e.empty())).toBe(false);
  });

  it.each(SLUGS)("'%s': to'g'ri namuna yaroqli", (slug) => {
    expect(getEngine(slug)!.isValid(VALID[slug])).toBe(true);
  });

  it.each(SLUGS)("'%s': noto'g'ri namuna rad etiladi", (slug) => {
    expect(getEngine(slug)!.isValid(INVALID[slug])).toBe(false);
  });
});
