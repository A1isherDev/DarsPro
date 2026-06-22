"use client";

import { motion } from "framer-motion";
import { BarChart3, Gamepad2, History, Star, Trophy } from "lucide-react";
import { useEffect, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/store";
import type { UserGameHistory, UserStats } from "@/types/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [history, setHistory] = useState<UserGameHistory[]>([]);

  useEffect(() => {
    api.get<UserStats>("/users/me/stats").then((r) => setStats(r.data));
    api
      .get<{ results: UserGameHistory[] }>("/users/me/history")
      .then((r) => setHistory(r.data.results ?? []));
  }, []);

  const cards = [
    { label: "O'ynalgan o'yinlar", value: stats?.total_games ?? 0, icon: Gamepad2, tint: "bg-answer-2/15 text-answer-2" },
    { label: "Umumiy ball", value: stats?.total_score ?? 0, icon: Star, tint: "bg-answer-3/15 text-answer-3" },
    { label: "O'rtacha ball", value: stats?.avg_score ?? 0, icon: BarChart3, tint: "bg-primary/15 text-primary" },
    { label: "Eng yaxshi ball", value: stats?.best_score ?? 0, icon: Trophy, tint: "bg-accent/15 text-accent" },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-2xl font-bold">
          Salom, {user?.full_name || "o'qituvchi"}! 👋
        </h1>
        <p className="text-muted-foreground">Bugungi darslaringizga xush kelibsiz.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {cards.map((c, i) => (
          <motion.div
            key={c.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
          >
            <Card className="shadow-soft">
              <CardContent className="space-y-3 pt-5">
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${c.tint}`}>
                  <c.icon size={20} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{c.label}</p>
                  <p className="font-display text-3xl font-bold">{c.value}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="font-display">So'nggi o'yinlar</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <EmptyState
              icon={History}
              title="Hali o'yin o'ynalmagan"
              description="Kutubxonadan o'yin tanlab o'ynang — natijalar shu yerda ko'rinadi."
            />
          ) : (
            <ul className="divide-y divide-border">
              {history.map((g) => (
                <li key={g.id} className="flex justify-between py-2.5 text-sm">
                  <span className="font-medium">{g.content_title}</span>
                  <span className="text-muted-foreground">
                    {g.score} ball · {new Date(g.played_at).toLocaleDateString("uz")}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
