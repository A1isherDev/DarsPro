"use client";

import { motion } from "framer-motion";
import Link from "next/link";

import { Button } from "@/components/ui/button";

const ENGINES = [
  { emoji: "❓", name: "Quiz", color: "bg-answer-1/15" },
  { emoji: "🔗", name: "Matching", color: "bg-answer-2/15" },
  { emoji: "🃏", name: "Flashcard", color: "bg-answer-3/15" },
  { emoji: "🎡", name: "Aylanma", color: "bg-answer-4/15" },
  { emoji: "🧠", name: "Xotira", color: "bg-primary/15" },
  { emoji: "🔤", name: "So'z izlash", color: "bg-accent/15" },
];

export default function HomePage() {
  return (
    <main className="bg-app-gradient min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center gap-10 px-6 py-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-block rounded-full bg-primary/12 px-4 py-1 text-sm font-semibold text-primary">
            O'zbekiston maktablari uchun
          </span>
          <h1 className="mt-4 font-display text-5xl font-extrabold tracking-tight sm:text-6xl">
            DarsPro
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
            Tayyor o'yinlar va kontent kutubxonasi. Savollaringizni kiriting —
            o'yin o'zi tayyor bo'ladi, sinf jonlanadi. 🎮
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-3 gap-3 sm:grid-cols-6"
          initial="hidden"
          animate="show"
          variants={{ show: { transition: { staggerChildren: 0.07 } } }}
        >
          {ENGINES.map((e) => (
            <motion.div
              key={e.name}
              variants={{
                hidden: { opacity: 0, scale: 0.7 },
                show: { opacity: 1, scale: 1 },
              }}
              className={`flex flex-col items-center gap-1 rounded-2xl ${e.color} px-3 py-4 shadow-soft`}
            >
              <span className="text-3xl">{e.emoji}</span>
              <span className="text-xs font-semibold">{e.name}</span>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          className="flex flex-col items-center gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex flex-wrap justify-center gap-3">
            <Link href="/register">
              <Button size="lg">Bepul boshlash</Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline">
                Kirish
              </Button>
            </Link>
            <Link href="/pricing">
              <Button size="lg" variant="ghost">
                Tariflar
              </Button>
            </Link>
          </div>
          <p className="text-sm text-muted-foreground">
            O'quvchimisiz?{" "}
            <Link href="/play" className="font-semibold text-primary underline">
              O'yin kodi bilan kiring →
            </Link>
          </p>
        </motion.div>
      </div>
    </main>
  );
}
