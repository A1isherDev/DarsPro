import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { QuizPlay } from "@/components/engines/Quiz/Play";
import type { QuizData } from "@/types/engines";

const DATA: QuizData = {
  questions: [
    {
      text: "Poytaxt qaysi?",
      image: null,
      options: ["Toshkent", "Samarqand"],
      answer: 0,
      time_limit: 30,
    },
  ],
};

describe("QuizPlay", () => {
  it("savol va variantlarni ko'rsatadi", () => {
    render(<QuizPlay data={DATA} />);
    expect(screen.getByText("Poytaxt qaysi?")).toBeInTheDocument();
    expect(screen.getByText("Toshkent")).toBeInTheDocument();
  });

  it("to'g'ri javob tanlansa, yakunlanganda ball > 0 bilan tugaydi", () => {
    const onFinish = vi.fn();
    render(<QuizPlay data={DATA} onFinish={onFinish} />);
    fireEvent.click(screen.getByText("Toshkent")); // to'g'ri javob
    fireEvent.click(screen.getByText("Yakunlash")); // yagona savol -> tugatish
    expect(onFinish).toHaveBeenCalledTimes(1);
    expect(onFinish.mock.calls[0][0]).toBeGreaterThan(0);
  });
});
