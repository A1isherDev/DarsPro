"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Celebrate } from "@/components/ui/celebrate";
import { Input, Label } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { BUILDABLE_ENGINES, getEngine } from "@/components/engines/registry";
import { apiError } from "@/lib/api";
import {
  createItem,
  fetchEngines,
  fetchGrades,
  fetchItem,
  fetchSubjects,
  fetchTopics,
  updateItem,
} from "@/lib/content";
import type { EngineSlug } from "@/types/engines";
import type { GameEngine, Grade, Subject, Topic } from "@/types/api";

function BuilderInner() {
  const router = useRouter();
  const editId = useSearchParams().get("edit");
  const editing = !!editId;

  const [engines, setEngines] = useState<GameEngine[]>([]);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);

  const [engineSlug, setEngineSlug] = useState<EngineSlug>("quiz");
  const [title, setTitle] = useState("");
  const [grade, setGrade] = useState("");
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [data, setData] = useState<unknown>(() => getEngine("quiz")!.empty());

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(!editing);

  useEffect(() => {
    fetchEngines().then(setEngines);
    fetchGrades().then(setGrades);
    fetchSubjects().then(setSubjects);
  }, []);

  // Tahrirlash rejimi: mavjud kontentni yuklash
  useEffect(() => {
    if (!editId) return;
    fetchItem(editId)
      .then((it) => {
        setEngineSlug(it.engine_slug);
        setTitle(it.title);
        setTopic(it.topic);
        setData(it.data);
        setLoaded(true);
      })
      .catch((e) => {
        setError(apiError(e));
        setLoaded(true);
      });
  }, [editId]);

  useEffect(() => {
    if (editing || (!grade && !subject)) {
      if (!editing) setTopics([]);
      return;
    }
    fetchTopics({
      grade: grade ? Number(grade) : undefined,
      subject: subject || undefined,
    }).then(setTopics);
  }, [grade, subject, editing]);

  const engineModule = getEngine(engineSlug);
  const engineId = useMemo(
    () => engines.find((e) => e.slug === engineSlug)?.id,
    [engines, engineSlug]
  );

  function changeEngine(slug: EngineSlug) {
    setEngineSlug(slug);
    setData(getEngine(slug)!.empty());
  }

  const canSave =
    loaded &&
    title.trim().length > 0 &&
    !!topic &&
    !!engineModule?.isValid(data) &&
    (editing || !!engineId);

  async function save() {
    if (!canSave) return;
    setSaving(true);
    setError(null);
    try {
      if (editing && editId) {
        await updateItem(editId, { title, data });
      } else {
        await createItem({ title, topic, engine: engineId!, data });
      }
      setSuccess(true);
    } catch (e) {
      setError(apiError(e));
    } finally {
      setSaving(false);
    }
  }

  if (success) {
    return (
      <div className="mx-auto max-w-lg space-y-4">
        <Celebrate
          title={editing ? "Saqlandi!" : "Yuborildi!"}
          subtitle={
            editing
              ? "O'zgarishlar saqlandi. Rad etilgan bo'lsa, qayta ko'rib chiqishga yuboriladi."
              : "O'yiningiz ko'rib chiqish uchun yuborildi. Tasdiqlangach kutubxonada paydo bo'ladi."
          }
        />
        <div className="flex justify-center gap-2">
          <Button onClick={() => router.push("/my-content")}>
            Mening kontentim
          </Button>
          <Button variant="outline" onClick={() => router.push("/library")}>
            Kutubxona
          </Button>
        </div>
      </div>
    );
  }

  if (!loaded) {
    return <p className="text-muted-foreground">Yuklanmoqda…</p>;
  }

  const Builder = engineModule?.Builder;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold">
          {editing ? "O'yinni tahrirlash" : "O'yin yaratish"}
        </h1>
        <p className="text-muted-foreground">
          {editing
            ? "Sarlavha va kontentni o'zgartiring."
            : "Savollaringizni kiriting — o'yin tayyor bo'ladi."}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label>O'yin turi</Label>
          <Select
            value={engineSlug}
            disabled={editing}
            onChange={(e) => changeEngine(e.target.value as EngineSlug)}
          >
            {BUILDABLE_ENGINES.map((en) => (
              <option key={en.slug} value={en.slug}>
                {en.name}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label>Sarlavha</Label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Masalan: Hujayra tuzilishi"
          />
        </div>

        {!editing && (
          <>
            <div className="space-y-1.5">
              <Label>Sinf</Label>
              <Select value={grade} onChange={(e) => setGrade(e.target.value)}>
                <option value="">Tanlang</option>
                {grades.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Fan</Label>
              <Select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              >
                <option value="">Tanlang</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.icon} {s.name}
                  </option>
                ))}
              </Select>
            </div>
            <div className="space-y-1.5 sm:col-span-2">
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
          </>
        )}
      </div>

      {editing && (
        <p className="text-sm text-muted-foreground">
          O'yin turi va mavzu tahrirlashda o'zgartirilmaydi.
        </p>
      )}

      <div>
        <h2 className="mb-3 text-lg font-semibold">Kontent</h2>
        {Builder && <Builder value={data} onChange={setData} />}
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <div className="flex justify-end gap-2">
        <Button disabled={!canSave || saving} onClick={save}>
          {saving
            ? "Saqlanmoqda…"
            : editing
            ? "Saqlash"
            : "Ko'rib chiqishga yuborish"}
        </Button>
      </div>
    </div>
  );
}

export default function BuilderPage() {
  return (
    <Suspense fallback={<p className="text-muted-foreground">Yuklanmoqda…</p>}>
      <BuilderInner />
    </Suspense>
  );
}
