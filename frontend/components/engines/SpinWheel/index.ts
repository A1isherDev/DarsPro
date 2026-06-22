import type { EngineDataMap } from "@/types/engines";
import type { EngineModule } from "../types";
import { SpinWheelBuilder } from "./Builder";
import { SpinWheelPlay } from "./Play";

type SpinData = EngineDataMap["spin_wheel"];

export const SpinWheelEngine: EngineModule<SpinData> = {
  slug: "spin_wheel",
  name: "Aylanma g'ildirak",
  empty: () => ({ items: ["", ""], type: "students" }),
  isValid: (d) =>
    d.items.length >= 2 && d.items.every((i) => i.trim().length > 0),
  Play: SpinWheelPlay,
  Builder: SpinWheelBuilder,
};
