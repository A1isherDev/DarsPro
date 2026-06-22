"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { playSound } from "@/lib/sound";
import { api } from "@/lib/api";
import { SessionSocket, type ServerEvent } from "@/lib/socket";
import type { SessionMode } from "@/types/api";

type Phase = "name" | "waiting" | "question" | "answered" | "ended";

interface CurrentQuestion {
  index: number;
  text: string;
  image: string | null;
  options: string[];
  timeLimit: number;
}

interface Rank {
  name: string;
  score: number;
  team: number | null;
}

const TILE = ["bg-answer-1", "bg-answer-2", "bg-answer-3", "bg-answer-4"];
const SHAPE = ["▲", "◆", "●", "■"];
const MEDAL = ["🥇", "🥈", "🥉"];

export default function StudentPlayPage({
  params,
}: {
  params: { join_code: string };
}) {
  const joinCode = params.join_code;
  const sockRef = useRef<SessionSocket | null>(null);

  const [phase, setPhase] = useState<Phase>("name");
  const [name, setName] = useState("");
  const [reconnecting, setReconnecting] = useState(false);
  const [team, setTeam] = useState("1");
  const [mode, setMode] = useState<SessionMode>("class");
  const [contentTitle, setContentTitle] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const [question, setQuestion] = useState<CurrentQuestion | null>(null);
  const [remaining, setRemaining] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [lastResult, setLastResult] = useState<{ correct: boolean; delta: number } | null>(null);
  const [leaderboard, setLeaderboard] = useState<Rank[]>([]);
  const [myScore, setMyScore] = useState(0);

  useEffect(() => {
    api
      .get(`/sessions/${joinCode}`)
      .then((r) => {
        setMode(r.data.mode);
        setContentTitle(r.data.content_title ?? "");
        if (r.data.status === "ended") setError("Bu o'yin allaqachon tugagan.");
      })
      .catch(() => setError("Bunday o'yin topilmadi."));
  }, [joinCode]);

  const isTeamMode = mode === "team" || mode === "pair";

  useEffect(() => {
    if (phase !== "question" || picked !== null) return;
    if (remaining <= 0) return;
    const t = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(t);
  }, [phase, remaining, picked]);

  useEffect(() => {
    return () => sockRef.current?.close();
  }, []);

  function handleEvent(ev: ServerEvent) {
    switch (ev.type) {
      case "question_show": {
        const q = ev.question as {
          text?: string;
          options?: string[];
          image?: string | null;
        };
        setQuestion({
          index: ev.index,
          text: q.text ?? "",
          image: q.image ?? null,
          options: q.options ?? [],
          timeLimit: ev.time_limit,
        });
        setRemaining(ev.time_limit);
        setPicked(null);
        setLastResult(null);
        setPhase("question");
        break;
      }
      case "answer_result":
        setLastResult({ correct: ev.correct, delta: ev.score_delta });
        setMyScore((s) => s + ev.score_delta);
        setPhase("answered");
        playSound(ev.correct ? "correct" : "wrong");
        break;
      case "leaderboard_update":
        setLeaderboard(ev.rankings);
        break;
      case "game_ended":
        setLeaderboard(ev.final_results);
        setPhase("ended");
        playSound("win");
        break;
      case "error":
        setError(ev.detail);
        break;
    }
  }

  function join(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    const teamNumber = isTeamMode ? Number(team) || 1 : null;
    const sock = new SessionSocket(joinCode, {
      onMessage: handleEvent,
      onOpen: () => {
        setReconnecting(false);
        sock.send({
          type: "player_join",
          display_name: name.trim(),
          team_number: teamNumber,
        });
      },
      onReconnecting: () => setReconnecting(true),
      onClose: (code) => {
        if (code === 4404) setError("Bunday o'yin topilmadi.");
      },
    });
    sock.connect();
    sockRef.current = sock;
    setPhase("waiting");
  }

  function answer(optionIndex: number) {
    if (!question || picked !== null) return;
    setPicked(optionIndex);
    sockRef.current?.send({
      type: "answer_submit",
      question_index: question.index,
      answer: optionIndex,
      time_taken: question.timeLimit - remaining,
    });
  }

  // --- name fazasi ---
  if (phase === "name") {
    return (
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="font-display text-2xl">O'yinga qo'shilish 🎮</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              {contentTitle && (
                <>
                  <span className="font-semibold text-foreground">{contentTitle}</span>
                  {" · "}
                </>
              )}
              Kod: <span className="font-mono font-bold text-primary">{joinCode}</span>
              {isTeamMode && (
                <span className="ml-1">· {mode === "pair" ? "Juft" : "Jamoa"} rejimi</span>
              )}
            </p>
            <form onSubmit={join} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="name">Ismingiz</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ism Familiya"
                  maxLength={64}
                  autoFocus
                />
              </div>
              {isTeamMode && (
                <div className="space-y-1.5">
                  <Label htmlFor="team">Jamoa raqami</Label>
                  <Input
                    id="team"
                    type="number"
                    min={1}
                    max={20}
                    value={team}
                    onChange={(e) => setTeam(e.target.value)}
                  />
                </div>
              )}
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" size="lg" className="w-full" disabled={!!error && !name}>
                Qo'shilish
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  if (phase === "waiting") {
    return (
      <Card className="shadow-card">
        <CardContent className="flex flex-col items-center gap-3 pt-10 pb-10 text-center">
          <motion.div
            className="text-5xl"
            animate={{ y: [0, -10, 0] }}
            transition={{ repeat: Infinity, duration: 1.6 }}
          >
            ⏳
          </motion.div>
          <p className="font-display text-lg font-semibold">Kutib turing…</p>
          <p className="text-sm text-muted-foreground">
            O'qituvchi o'yinni boshlashini kuting.
          </p>
          {reconnecting && (
            <p className="text-sm text-warning-foreground">Qayta ulanmoqda…</p>
          )}
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>
    );
  }

  if (phase === "ended") {
    return (
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
        <Card className="shadow-card">
          <CardContent className="space-y-4 pt-6">
            <div className="text-center">
              <motion.div
                className="text-5xl"
                initial={{ scale: 0 }}
                animate={{ scale: 1, rotate: [0, -10, 10, 0] }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                🎉
              </motion.div>
              <h2 className="mt-2 font-display text-2xl font-bold">O'yin tugadi!</h2>
              <p className="text-muted-foreground">
                Sizning ballingiz: <span className="font-bold text-primary">{myScore}</span>
              </p>
            </div>
            <Leaderboard rankings={leaderboard} mode={mode} />
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  // question / answered
  return (
    <div className="space-y-4">
      <AnimatePresence>
        {reconnecting && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="rounded-xl bg-warning/20 px-3 py-2 text-center text-sm font-medium text-warning-foreground"
          >
            Aloqa uzildi — qayta ulanmoqda…
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center justify-between text-sm">
        <span className="font-semibold text-muted-foreground">Ball: {myScore}</span>
        {phase === "question" && (
          <motion.span
            key={remaining}
            initial={{ scale: 1.3 }}
            animate={{ scale: 1 }}
            className={cn(
              "rounded-full px-2.5 py-0.5 font-bold tabular-nums",
              remaining <= 5 ? "bg-destructive/15 text-destructive" : "bg-muted"
            )}
          >
            ⏱ {remaining}s
          </motion.span>
        )}
      </div>

      {question && (
        <Card>
          <CardContent className="pt-6">
            {question.image && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={question.image}
                alt=""
                className="mb-4 max-h-56 w-full rounded-xl object-contain"
              />
            )}
            <h2 className="mb-5 font-display text-xl font-bold">{question.text}</h2>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {question.options.map((opt, i) => (
                <motion.button
                  key={i}
                  onClick={() => answer(i)}
                  disabled={picked !== null}
                  whileTap={{ scale: 0.96 }}
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-4 py-4 text-left font-semibold text-white shadow-soft transition-opacity",
                    TILE[i % TILE.length],
                    picked !== null && picked !== i && "opacity-40"
                  )}
                >
                  <span className="text-lg opacity-90">{SHAPE[i % SHAPE.length]}</span>
                  <span className="flex-1">{opt}</span>
                </motion.button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <AnimatePresence>
        {phase === "answered" && lastResult && (
          <motion.div
            key="result"
            initial={{ opacity: 0, scale: 0.85 }}
            animate={
              lastResult.correct
                ? { opacity: 1, scale: 1 }
                : { opacity: 1, scale: 1, x: [0, -8, 8, -8, 8, 0] }
            }
            exit={{ opacity: 0 }}
          >
            <Card
              className={cn(
                lastResult.correct
                  ? "border-success/50 bg-success/10"
                  : "border-destructive/50 bg-destructive/10"
              )}
            >
              <CardContent className="pt-5 text-center">
                <p className="text-3xl">{lastResult.correct ? "🎉" : "😕"}</p>
                <p
                  className={cn(
                    "mt-1 font-display text-lg font-bold",
                    lastResult.correct ? "text-success" : "text-destructive"
                  )}
                >
                  {lastResult.correct ? `To'g'ri! +${lastResult.delta}` : "Noto'g'ri"}
                </p>
                <p className="mt-1 text-sm text-muted-foreground">Keyingi savolni kuting…</p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {leaderboard.length > 0 && <Leaderboard rankings={leaderboard} mode={mode} />}
    </div>
  );
}

function Leaderboard({
  rankings,
  mode = "class",
}: {
  rankings: Rank[];
  mode?: SessionMode;
}) {
  const teamMode = mode === "team" || mode === "pair";

  let rows: { label: string; score: number }[];
  if (teamMode) {
    const totals = new Map<number, number>();
    for (const r of rankings) {
      const t = r.team ?? 0;
      totals.set(t, (totals.get(t) ?? 0) + r.score);
    }
    rows = [...totals.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([t, score]) => ({ label: `${t}-jamoa`, score }));
  } else {
    rows = rankings.map((r) => ({ label: r.name, score: r.score }));
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-display text-base">
          {teamMode ? "Jamoalar reytingi" : "Reyting"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="space-y-1.5">
          {rows.slice(0, 10).map((r, i) => (
            <motion.li
              key={r.label}
              layout
              className={cn(
                "flex items-center justify-between rounded-lg px-3 py-1.5 text-sm",
                i < 3 ? "bg-muted font-semibold" : ""
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
      </CardContent>
    </Card>
  );
}
