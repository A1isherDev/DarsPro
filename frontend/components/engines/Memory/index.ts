import type { EngineDataMap } from "@/types/engines";
import type { EngineModule } from "../types";
import { MemoryBuilder } from "./Builder";
import { MemoryPlay } from "./Play";

type MemoryData = EngineDataMap["memory"];

export const MemoryEngine: EngineModule<MemoryData> = {
  slug: "memory",
  name: "Xotira (juftlik)",
  empty: () => ({ pairs: [{ a: "", b: "" }] }),
  isValid: (d) =>
    d.pairs.length > 0 &&
    d.pairs.every((p) => p.a.trim().length > 0 && p.b.trim().length > 0),
  Play: MemoryPlay,
  Builder: MemoryBuilder,
};
