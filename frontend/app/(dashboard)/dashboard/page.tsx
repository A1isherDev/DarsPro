"use client";

import { motion } from "framer-motion";
import { BarChart3, Gamepad2, History, Star, Trophy } from "lucide-react";
import { useEffect, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/store";
import type { UserGameHistory, UserStats } from "@/types/api";

interface TeachingStats {
  total_sessions: number;
  ended_sessions: number;
  total_participants: number;
  avg_participant_score: number;
  top_content: { title: string; sessions: number }[];
}

interface Badge {
  key: string;
  label: string;
  emoji: string;
  current: number;
  target: number;
  earned: boolean;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [history, setHistory] = useState<UserGameHistory[]>([]);
  const [teaching, setTeaching] = useState<TeachingStats | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);

  useEffect(() => {
    api.get<UserStats>("/users/me/stats").then((r) => setStats(r.data));
    api
      .get<{ results: UserGameHistory[] }>("/users/me/history")
      .then((r) => setHistory(r.data.results ?? []));
    api
      .get<TeachingStats>("/users/me/teaching-stats")
      .then((r) => setTeaching(r.data))
      .catch(() => {});
    api
      .get<{ badges: Badge[] }>("/users/me/achievements")
      .then((r) => setBadges(r.data.badges))
      .catch(() => {});
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

      {badges.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="font-display">Yutuqlar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {badges.map((b, i) => (
                <motion.div
                  key={b.key}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className={cn(
                    "flex items-center gap-3 rounded-xl border p-3",
                    b.earned
                      ? "border-primary/30 bg-primary/5"
                      : "border-border opacity-60"
                  )}
                >
                  <span className={cn("text-2xl", !b.earned && "grayscale")}>
                    {b.emoji}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">{b.label}</p>
                    <p className="text-xs text-muted-foreground">
                      {b.earned ? "Olindi ✓" : `${b.current}/${b.target}`}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {teaching && teaching.total_sessions > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="font-display">Sinf sessiyalari</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-6 text-sm">
              <div>
                <p className="text-2xl font-bold">{teaching.total_sessions}</p>
                <p className="text-muted-foreground">Sessiya</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{teaching.total_participants}</p>
                <p className="text-muted-foreground">O'quvchi qatnashdi</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{teaching.avg_participant_score}</p>
                <p className="text-muted-foreground">O'rtacha ball</p>
              </div>
            </div>
            {teaching.top_content.length > 0 && (
              <div>
                <p className="mb-1 text-sm font-medium">Eng ko'p o'tkazilgan:</p>
                <ul className="space-y-1">
                  {teaching.top_content.map((t) => (
                    <li key={t.title} className="flex justify-between text-sm">
                      <span className="truncate pr-2">{t.title}</span>
                      <span className="text-muted-foreground">{t.sessions}×</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
