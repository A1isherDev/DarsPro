"use client";

import { motion } from "framer-motion";
import { Download, Printer } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, apiError, tokenStore } from "@/lib/api";
import { SessionSocket, type ServerEvent } from "@/lib/socket";
import { cn } from "@/lib/utils";
import type { GameSession } from "@/types/api";

const MEDAL = ["🥇", "🥈", "🥉"];

interface Rank {
  name: string;
  score: number;
  team: number | null;
}

interface QuestionStat {
  index: number;
  text: string;
  correct: number;
  total: number;
  accuracy: number;
  avg_time: number;
}

export default function HostRoomPage({ params }: { params: { code: string } }) {
  const joinCode = params.code;
  const sockRef = useRef<SessionSocket | null>(null);

  const [session, setSession] = useState<GameSession | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [started, setStarted] = useState(false);
  const [ended, setEnded] = useState(false);
  const [players, setPlayers] = useState<string[]>([]);
  const [leaderboard, setLeaderboard] = useState<Rank[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number | null>(null);
  const [report, setReport] = useState<QuestionStat[] | null>(null);

  // O'yin tugagach savol bo'yicha hisobotni yuklaymiz
  useEffect(() => {
    if (!ended || !session) return;
    api
      .get(`/sessions/${session.id}/report`)
      .then((r) => setReport(r.data.question_stats))
      .catch(() => {});
  }, [ended, session]);

  async function downloadCsv() {
    if (!session) return;
    try {
      const r = await api.get(`/sessions/${session.id}/results.csv`, {
        responseType: "blob",
      });
      const url = URL.createObjectURL(r.data as Blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `darspro-${session.join_code}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(apiError(e));
    }
  }

  useEffect(() => {
    api
      .get<GameSession>(`/sessions/${joinCode}`)
      .then((r) => {
        setSession(r.data);
        setStarted(r.data.status !== "waiting");
        setEnded(r.data.status === "ended");
      })
      .catch((e) => setError(apiError(e)));
  }, [joinCode]);

  useEffect(() => {
    if (!session) return;
    const sock = new SessionSocket(
      joinCode,
      {
        onMessage: handleEvent,
        onOpen: () => setConnected(true),
        onClose: () => setConnected(false),
      },
      tokenStore.access
    );
    sock.connect();
    sockRef.current = sock;
    return () => sock.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.id]);

  function handleEvent(ev: ServerEvent) {
    switch (ev.type) {
      case "player_joined":
        setPlayers((p) =>
          p.includes(ev.display_name) ? p : [...p, ev.display_name]
        );
        break;
      case "question_show":
        setCurrentIndex(ev.index);
        break;
      case "leaderboard_update":
        setLeaderboard(ev.rankings);
        break;
      case "game_ended":
        setLeaderboard(ev.final_results);
        setEnded(true);
        break;
      case "error":
        setError(ev.detail);
        break;
    }
  }

  async function start() {
    if (!session) return;
    try {
      await api.patch(`/sessions/${session.id}/start`);
    } catch (e) {
      setError(apiError(e));
      return;
    }
    setStarted(true);
    sockRef.current?.send({ type: "host_next" });
  }

  function nextQuestion() {
    sockRef.current?.send({ type: "host_next" });
  }

  function end() {
    sockRef.current?.send({ type: "host_end" });
  }

  if (error && !session)
    return <p className="text-destructive">{error}</p>;
  if (!session) return <p className="text-muted-foreground">Yuklanmoqda…</p>;

  const teamMode = session.mode === "team" || session.mode === "pair";
  const modeLabel =
    session.mode === "team"
      ? "Jamoa"
      : session.mode === "pair"
      ? "Juft"
      : "Sinf";

  // Jamoa rejimida reyting jamoalar bo'yicha yig'iladi
  let leaderRows: { label: string; score: number }[];
  if (teamMode) {
    const totals = new Map<number, number>();
    for (const r of leaderboard) {
      const t = r.team ?? 0;
      totals.set(t, (totals.get(t) ?? 0) + r.score);
    }
    leaderRows = [...totals.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([t, score]) => ({ label: `${t}-jamoa`, score }));
  } else {
    leaderRows = leaderboard.map((r) => ({ label: r.name, score: r.score }));
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold">{session.content_title}</h1>
          <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
            <span
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold",
                connected
                  ? "bg-success/15 text-success"
                  : "bg-destructive/15 text-destructive"
              )}
            >
              <span
                className={cn(
                  "h-2 w-2 rounded-full",
                  connected ? "bg-success" : "bg-destructive"
                )}
              />
              {connected ? "Ulangan" : "Ulanmagan"}
            </span>
            <span>· {session.engine_slug} · {modeLabel} rejimi</span>
          </div>
        </div>
      </div>

      <Card className="overflow-hidden border-primary/30 bg-primary/5">
        <CardContent className="flex flex-col items-center gap-2 py-8">
          <p className="text-sm font-medium text-muted-foreground">O'yin kodi</p>
          <motion.p
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 260 }}
            className="font-mono text-5xl font-bold tracking-widest text-primary sm:text-6xl"
          >
            {session.join_code}
          </motion.p>
          <p className="text-sm text-muted-foreground">
            O'quvchilar play sahifasida shu kodni kiritadi
          </p>
        </CardContent>
      </Card>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <div className="flex gap-2">
        {!started && !ended && (
          <Button onClick={start} disabled={!connected}>
            O'yinni boshlash
          </Button>
        )}
        {started && !ended && (
          <>
            <Button onClick={nextQuestion}>Keyingi savol</Button>
            <Button variant="destructive" onClick={end}>
              Tugatish
            </Button>
          </>
        )}
        {currentIndex !== null && !ended && (
          <span className="flex items-center text-sm text-muted-foreground">
            Joriy savol: {currentIndex + 1}
          </span>
        )}
        {ended && (
          <>
            <span className="flex items-center font-semibold">O'yin tugadi ✅</span>
            <Button variant="outline" onClick={downloadCsv}>
              <Download size={16} /> CSV yuklab olish
            </Button>
            <Button variant="outline" onClick={() => window.print()}>
              <Printer size={16} /> Chop etish / PDF
            </Button>
          </>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              O'quvchilar ({players.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {players.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Hali hech kim qo'shilmadi.
              </p>
            ) : (
              <ul className="flex flex-wrap gap-2">
                {players.map((p, i) => (
                  <motion.li
                    key={i}
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ type: "spring", stiffness: 400, damping: 24 }}
                    className="rounded-full bg-primary/12 px-3 py-1 text-sm font-medium text-primary"
                  >
                    {p}
                  </motion.li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {teamMode ? "Jamoalar reytingi" : "Reyting"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {leaderboard.length === 0 ? (
              <p className="text-sm text-muted-foreground">Hali ball yo'q.</p>
            ) : (
              <ol className="space-y-1.5">
                {leaderRows.slice(0, 10).map((r, i) => (
                  <motion.li
                    key={r.label}
                    layout
                    className={cn(
                      "flex items-center justify-between rounded-lg px-3 py-1.5 text-sm",
                      i < 3 && "bg-muted font-semibold"
                    )}
                  >
                    <span className="flex items-center gap-2">
                      <span className="w-6 text-center">{MEDAL[i] ?? i + 1}</span>
                      {r.label}
                    </span>
                    <span className="font-bold tabular-nums">{r.score}</span>
                  </motion.li>
                ))}
              </ol>
            )}
          </CardContent>
        </Card>
      </div>

      {ended && report && report.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Savol bo'yicha tahlil</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {report.map((q) => (
              <div key={q.index} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="truncate pr-2 font-medium">
                    {q.index + 1}. {q.text}
                  </span>
                  <span className="shrink-0 tabular-nums text-muted-foreground">
                    {q.accuracy}% · {q.correct}/{q.total}
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className={cn(
                      "h-full rounded-full",
                      q.accuracy >= 70
                        ? "bg-success"
                        : q.accuracy >= 40
                        ? "bg-warning"
                        : "bg-destructive"
                    )}
                    style={{ width: `${q.accuracy}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
