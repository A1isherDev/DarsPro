"use client";

import { motion } from "framer-motion";
import {
  BookOpen,
  Copy,
  Heart,
  Library as LibraryIcon,
  Search,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Badge, Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input, Label } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { Select } from "@/components/ui/select";
import { CardSkeletonGrid } from "@/components/ui/skeleton";
import { api, apiError } from "@/lib/api";
import {
  cloneItem,
  fetchFavorites,
  fetchGrades,
  fetchItems,
  fetchPage,
  fetchSubjects,
  fetchTopics,
  setFavorite,
} from "@/lib/content";
import { LoadMore } from "@/components/shared/LoadMore";
import { useAuth } from "@/lib/store";
import type {
  ContentItemListEntry,
  Grade,
  SessionMode,
  Subject,
  Topic,
} from "@/types/api";

export default function LibraryPage() {
  const router = useRouter();
  const toast = useToast();
  const { user } = useAuth();
  const isFree = user?.effective_plan === "free";

  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [items, setItems] = useState<ContentItemListEntry[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  const [grade, setGrade] = useState("");
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [search, setSearch] = useState("");
  const [favOnly, setFavOnly] = useState(false);
  const [mode, setMode] = useState<SessionMode>("class");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGrades().then(setGrades);
    fetchSubjects().then(setSubjects);
  }, []);

  // grade/subject o'zgarsa — mavzularni yangilash
  useEffect(() => {
    setTopic("");
    setItems([]);
    if (!grade && !subject) {
      setTopics([]);
      return;
    }
    fetchTopics({
      grade: grade ? Number(grade) : undefined,
      subject: subject || undefined,
    }).then(setTopics);
  }, [grade, subject]);

  // favorit / topic / qidiruv o'zgarsa — kontentni yuklash (qidiruv debounce bilan)
  useEffect(() => {
    const q = search.trim();
    if (favOnly) {
      setLoading(true);
      fetchFavorites()
        .then((p) => {
          setItems(p.results);
          setNext(p.next);
        })
        .catch((e) => setError(apiError(e)))
        .finally(() => setLoading(false));
      return;
    }
    if (!topic && !q) {
      setItems([]);
      setNext(null);
      return;
    }
    const t = setTimeout(() => {
      setLoading(true);
      fetchItems({
        topic: topic || undefined,
        search: q || undefined,
      })
        .then((p) => {
          setItems(p.results);
          setNext(p.next);
        })
        .catch((e) => setError(apiError(e)))
        .finally(() => setLoading(false));
    }, q ? 300 : 0);
    return () => clearTimeout(t);
  }, [topic, search, favOnly]);

  async function toggleFav(item: ContentItemListEntry) {
    const next = !item.is_favorited;
    setItems((list) =>
      list.map((i) => (i.id === item.id ? { ...i, is_favorited: next } : i))
    );
    try {
      await setFavorite(item.id, next);
    } catch (e) {
      // qaytarish
      setItems((list) =>
        list.map((i) => (i.id === item.id ? { ...i, is_favorited: !next } : i))
      );
      setError(apiError(e));
    }
  }

  async function loadMore() {
    if (!next) return;
    setLoadingMore(true);
    try {
      const p = await fetchPage<ContentItemListEntry>(next);
      setItems((prev) => [...prev, ...p.results]);
      setNext(p.next);
    } catch (e) {
      setError(apiError(e));
    } finally {
      setLoadingMore(false);
    }
  }

  async function clone(item: ContentItemListEntry) {
    try {
      const copy = await cloneItem(item.id);
      toast.success("Nusxa yaratildi — tahrirlashingiz mumkin.");
      router.push(`/builder?edit=${copy.id}`);
    } catch (e) {
      toast.error(apiError(e));
    }
  }

  async function startSession(item: ContentItemListEntry) {
    setError(null);
    try {
      const { data } = await api.post("/sessions/", {
        content: item.id,
        mode,
      });
      router.push(`/sessions/${data.join_code}`);
    } catch (e) {
      setError(apiError(e));
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold">Kutubxona</h1>
        <p className="text-muted-foreground">Sinf va fan bo'yicha o'yinlarni toping.</p>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="O'yin nomi bo'yicha qidirish…"
            className="pl-9"
            disabled={favOnly}
          />
        </div>
        <Button
          variant={favOnly ? "default" : "outline"}
          onClick={() => setFavOnly((v) => !v)}
        >
          <Heart size={16} className={favOnly ? "fill-current" : ""} /> Sevimlilar
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="space-y-1.5">
          <Label>Sinf</Label>
          <Select value={grade} onChange={(e) => setGrade(e.target.value)}>
            <option value="">Barchasi</option>
            {grades.map((g) => (
              <option key={g.id} value={g.id}>
                {g.label}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label>Fan</Label>
          <Select value={subject} onChange={(e) => setSubject(e.target.value)}>
            <option value="">Barchasi</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.icon} {s.name}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label>Mavzu</Label>
          <Select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={topics.length === 0}
          >
            <option value="">
              {topics.length ? "Mavzuni tanlang" : "Avval sinf/fan tanlang"}
            </option>
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.title}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1.5">
          <Label>Sessiya rejimi</Label>
          <Select
            value={mode}
            onChange={(e) => setMode(e.target.value as SessionMode)}
            className="w-44"
          >
            <option value="class">Sinf</option>
            <option value="pair" disabled={isFree}>
              Juft{isFree ? " (Start+)" : ""}
            </option>
            <option value="team" disabled={isFree}>
              Jamoa{isFree ? " (Start+)" : ""}
            </option>
          </Select>
        </div>
        <p className="pb-2 text-xs text-muted-foreground">
          Kartochkadagi jonli-o'yin tugmasi tanlangan rejimda sessiya ochadi.
        </p>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {loading ? (
        <CardSkeletonGrid count={6} />
      ) : !favOnly && !topic && !search.trim() ? (
        <EmptyState
          icon={LibraryIcon}
          title="O'yin tanlash"
          description="Qidiruv yozing yoki sinf/fan/mavzuni tanlang — o'yinlar shu yerda paydo bo'ladi."
        />
      ) : items.length === 0 ? (
        <EmptyState
          icon={favOnly ? Heart : BookOpen}
          title={favOnly ? "Sevimlilar bo'sh" : "O'yin topilmadi"}
          description={
            favOnly
              ? "Yoqqan o'yinlaringizni yurakcha bilan belgilang."
              : "Boshqa so'rov/mavzuni sinab ko'ring yoki o'zingiz yarating."
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <motion.div
              key={item.id}
              whileHover={{ y: -4 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Card className="h-full shadow-soft transition-shadow hover:shadow-card">
                <CardContent className="space-y-3 pt-5">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-display font-semibold">{item.title}</h3>
                    <button
                      onClick={() => toggleFav(item)}
                      title="Sevimli"
                      className="shrink-0 text-muted-foreground transition-colors hover:text-accent"
                    >
                      <Heart
                        size={18}
                        className={
                          item.is_favorited ? "fill-accent text-accent" : ""
                        }
                      />
                    </button>
                  </div>
                  <Badge variant="primary">{item.engine_slug}</Badge>
                  <p className="text-xs text-muted-foreground">
                    {item.play_count} marta o'ynalgan
                  </p>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      className="flex-1"
                      onClick={() => router.push(`/solo/${item.id}`)}
                    >
                      O'ynash
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => startSession(item)}
                    >
                      {mode === "team"
                        ? "Jamoa o'yini"
                        : mode === "pair"
                        ? "Juft o'yin"
                        : "Sinf rejimi"}
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      title="Nusxalab tahrirlash"
                      onClick={() => clone(item)}
                    >
                      <Copy size={16} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
          <div className="sm:col-span-2 lg:col-span-3">
            <LoadMore next={next} onLoad={loadMore} loading={loadingMore} />
          </div>
        </div>
      )}
    </div>
  );
}
