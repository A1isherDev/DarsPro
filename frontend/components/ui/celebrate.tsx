"use client";

import { motion } from "framer-motion";

import { Card, CardContent } from "./card";

/** O'yin yakunlangandagi quvnoq banner (engine finish ekranlari uchun). */
export function Celebrate({
  emoji = "🎉",
  title,
  subtitle,
}: {
  emoji?: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
      <Card className="border-success/40 bg-success/5">
        <CardContent className="space-y-2 pt-6 pb-6 text-center">
          <motion.div
            className="text-5xl"
            initial={{ scale: 0 }}
            animate={{ scale: 1, rotate: [0, -12, 12, 0] }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            {emoji}
          </motion.div>
          <h2 className="font-display text-xl font-bold">{title}</h2>
          {subtitle && <p className="text-muted-foreground">{subtitle}</p>}
        </CardContent>
      </Card>
    </motion.div>
  );
}
