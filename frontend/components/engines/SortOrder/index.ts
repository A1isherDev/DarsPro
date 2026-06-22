import type { EngineDataMap } from "@/types/engines";
import type { EngineModule } from "../types";
import { SortOrderBuilder } from "./Builder";
import { SortOrderPlay } from "./Play";

type SortData = EngineDataMap["sort_order"];

export const SortOrderEngine: EngineModule<SortData> = {
  slug: "sort_order",
  name: "Tartiblash",
  empty: () => ({
    title: "",
    items: [
      { text: "", order: 1 },
      { text: "", order: 2 },
    ],
  }),
  isValid: (d) =>
    d.items.length >= 2 && d.items.every((i) => i.text.trim().length > 0),
  Play: SortOrderPlay,
  Builder: SortOrderBuilder,
};
