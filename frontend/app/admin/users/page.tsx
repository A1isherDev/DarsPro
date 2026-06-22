"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Badge, Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { api, apiError } from "@/lib/api";
import { fetchPage } from "@/lib/content";
import { LoadMore } from "@/components/shared/LoadMore";
import { useToast } from "@/components/ui/toast";
import { PLAN_LABELS } from "@/lib/utils";
import type { Paginated, Plan } from "@/types/api";

interface AdminUser {
  id: string;
  full_name: string;
  email: string;
  plan: Plan;
  plan_expires_at: string | null;
  is_active: boolean;
  is_staff: boolean;
  created_at: string;
}

const GRANTABLE: Plan[] = ["start", "pro", "max"];

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const toast = useToast();

  // har bir user uchun tanlangan plan/days
  const [draft, setDraft] = useState<Record<string, { plan: Plan; days: number }>>(
    {}
  );

  async function load() {
    setLoading(true);
    try {
      const { data } = await api.get<Paginated<AdminUser>>("/admin/users");
      setUsers(data.results);
      setNext(data.next);
    } catch (e) {
      setError(apiError(e));
    } finally {
      setLoading(false);
    }
  }

  async function loadMore() {
    if (!next) return;
    setLoadingMore(true);
    try {
      const data = await fetchPage<AdminUser>(next);
      setUsers((prev) => [...prev, ...data.results]);
      setNext(data.next);
    } catch (e) {
      setError(apiError(e));
    } finally {
      setLoadingMore(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function setUserDraft(id: string, patch: Partial<{ plan: Plan; days: number }>) {
    setDraft((d) => {
      const current = d[id] ?? { plan: "start" as Plan, days: 30 };
      return { ...d, [id]: { ...current, ...patch } };
    });
  }

  async function grant(id: string) {
    const g = draft[id] ?? { plan: "start" as Plan, days: 30 };
    setBusy(id);
    setError(null);
    try {
      const { data } = await api.patch<AdminUser>(`/admin/users/${id}/plan`, {
        plan: g.plan,
        days: g.days,
      });
      setUsers((list) => list.map((u) => (u.id === id ? data : u)));
      toast.success(`Tarif berildi: ${PLAN_LABELS[data.plan]}`);
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold">Foydalanuvchilar</h1>
        <p className="text-muted-foreground">Manual tarif berish va boshqarish.</p>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {loading ? (
        <p className="text-muted-foreground">Yuklanmoqda…</p>
      ) : (
        <div className="space-y-3">
          {users.map((u) => {
            const g = draft[u.id] ?? { plan: "start" as Plan, days: 30 };
            return (
              <Card key={u.id}>
                <CardContent className="flex flex-wrap items-center justify-between gap-3 pt-5">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">
                        {u.full_name || u.email}
                      </span>
                      <Badge>{PLAN_LABELS[u.plan]}</Badge>
                      {u.is_staff && <Badge>staff</Badge>}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {u.email}
                      {u.plan_expires_at &&
                        ` · tugaydi: ${new Date(
                          u.plan_expires_at
                        ).toLocaleDateString("uz")}`}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Select
                      value={g.plan}
                      onChange={(e) =>
                        setUserDraft(u.id, { plan: e.target.value as Plan })
                      }
                      className="w-28"
                    >
                      {GRANTABLE.map((p) => (
                        <option key={p} value={p}>
                          {PLAN_LABELS[p]}
                        </option>
                      ))}
                    </Select>
                    <Input
                      type="number"
                      min={1}
                      className="w-20"
                      value={g.days}
                      onChange={(e) =>
                        setUserDraft(u.id, { days: Number(e.target.value) || 30 })
                      }
                    />
                    <span className="text-xs text-muted-foreground">kun</span>
                    <Button
                      size="sm"
                      disabled={busy === u.id}
                      onClick={() => grant(u.id)}
                    >
                      Berish
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
          <LoadMore next={next} onLoad={loadMore} loading={loadingMore} />
        </div>
      )}
    </div>
  );
}
