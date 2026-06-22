import type { EngineDataMap } from "@/types/engines";
import type { EngineModule } from "../types";
import { FillBlankBuilder } from "./Builder";
import { FillBlankPlay } from "./Play";

type FillData = EngineDataMap["fill_blank"];

export const FillBlankEngine: EngineModule<FillData> = {
  slug: "fill_blank",
  name: "Bo'sh joyni to'ldirish",
  empty: () => ({ text: "", blanks: [], hints: [] }),
  isValid: (d) => {
    const count = (d.text ?? "").split("___").length - 1;
    return (
      count > 0 &&
      d.blanks.length === count &&
      d.blanks.every((b) => b.trim().length > 0)
    );
  },
  Play: FillBlankPlay,
  Builder: FillBlankBuilder,
};
