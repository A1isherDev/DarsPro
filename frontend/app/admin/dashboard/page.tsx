"use client";

import { useEffect, useState } from "react";
import { BookOpen, Clock, CreditCard, Radio, Users } from "lucide-react";

import { Badge, Card, CardContent } from "@/components/ui/card";
import { api, apiError } from "@/lib/api";
import { PLAN_LABELS } from "@/lib/utils";
import type { AdminStats } from "@/types/api";

const STATUS_LABELS: Record<string, string> = {
  draft: "Qoralama",
  pending: "Ko'rib chiqilmoqda",
  published: "Chop etilgan",
  rejected: "Rad etilgan",
};

const MODE_LABELS: Record<string, string> = {
  solo: "Yakka",
  class: "Sinf",
  pair: "Juft",
  team: "Jamoa",
};

function formatSom(n: number): string {
  return n.toLocaleString("uz-UZ") + " so'm";
}

function Kpi({
  icon: Icon,
  label,
  value,
  hint,
  tone = "primary",
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  hint?: string;
  tone?: "primary" | "success" | "accent" | "warning" | "info";
}) {
  const toneBg: Record<string, string> = {
    primary: "bg-primary/12 text-primary",
    success: "bg-success/15 text-success",
    accent: "bg-accent/12 text-accent",
    warning: "bg-warning/20 text-warning-foreground",
    info: "bg-info/15 text-info",
  };
  return (
    <Card>
      <CardContent className="flex items-center gap-4 pt-6">
        <div className={`grid h-12 w-12 place-items-center rounded-xl ${toneBg[tone]}`}>
          <Icon size={22} />
        </div>
        <div className="min-w-0">
          <p className="font-display text-2xl font-bold leading-tight">{value}</p>
          <p className="truncate text-sm text-muted-foreground">{label}</p>
          {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
        </div>
      </CardContent>
    </Card>
  );
}

function Breakdown({
  title,
  data,
  labels,
}: {
  title: string;
  data: Record<string, number>;
  labels?: Record<string, string>;
}) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((s, [, n]) => s + n, 0) || 1;
  return (
    <Card>
      <CardContent className="pt-6">
        <h3 className="mb-4 font-semibold">{title}</h3>
        {entries.length === 0 ? (
          <p className="text-sm text-muted-foreground">Ma'lumot yo'q.</p>
        ) : (
          <div className="space-y-3">
            {entries.map(([key, n]) => (
              <div key={key}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="capitalize">{labels?.[key] ?? key}</span>
                  <span className="font-semibold tabular-nums">{n}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${Math.round((n / total) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<AdminStats>("/admin/stats")
      .then(({ data }) => setStats(data))
      .catch((e) => setError(apiError(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-muted-foreground">Yuklanmoqda…</p>;
  }
  if (error || !stats) {
    return <p className="text-sm text-destructive">{error ?? "Xatolik."}</p>;
  }

  const { users, subscriptions, content, sessions } = stats;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Platforma ko'rsatkichlari — real vaqt hisobi.
        </p>
      </div>

      {/* KPI kartalari */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Kpi
          icon={Users}
          label="Foydalanuvchilar"
          value={users.total}
          hint={`+${users.new_week} (7 kun)`}
        />
        <Kpi
          icon={CreditCard}
          label="Faol obunalar"
          value={subscriptions.active}
          hint={`${subscriptions.expiring_week} ta 7 kunda tugaydi`}
          tone="success"
        />
        <Kpi
          icon={CreditCard}
          label="Taxminiy MRR"
          value={formatSom(subscriptions.mrr)}
          hint="oylik takroriy daromad"
          tone="accent"
        />
        <Kpi
          icon={BookOpen}
          label="Jami kontent"
          value={content.total}
          hint={`${content.total_plays} marta o'ynalgan`}
          tone="info"
        />
        <Kpi
          icon={Clock}
          label="Ko'rib chiqishda"
          value={content.pending}
          hint="tasdiqlash kutilmoqda"
          tone="warning"
        />
        <Kpi
          icon={Radio}
          label="Jami sessiyalar"
          value={sessions.total}
          hint={`${sessions.participants} o'quvchi, ${sessions.solo_games} solo`}
        />
      </div>

      {/* Breakdown bloklar */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Breakdown
          title="Foydalanuvchilar — tarif bo'yicha"
          data={users.by_plan}
          labels={PLAN_LABELS}
        />
        <Breakdown
          title="Obunalar — tarif bo'yicha"
          data={subscriptions.by_plan}
          labels={PLAN_LABELS}
        />
        <Breakdown
          title="Kontent — holat bo'yicha"
          data={content.by_status}
          labels={STATUS_LABELS}
        />
        <Breakdown title="Kontent — engine bo'yicha" data={content.by_engine} />
        <Breakdown
          title="Sessiyalar — rejim bo'yicha"
          data={sessions.by_mode}
          labels={MODE_LABELS}
        />

        {/* Eng ko'p o'ynalgan */}
        <Card>
          <CardContent className="pt-6">
            <h3 className="mb-4 font-semibold">Eng ko'p o'ynalgan</h3>
            {content.top_played.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Hali o'yin o'ynalmagan.
              </p>
            ) : (
              <ol className="space-y-2">
                {content.top_played.map((item, i) => (
                  <li
                    key={item.id}
                    className="flex items-center justify-between gap-3 text-sm"
                  >
                    <span className="flex min-w-0 items-center gap-2">
                      <span className="text-muted-foreground">{i + 1}.</span>
                      <span className="truncate">{item.title}</span>
                    </span>
                    <Badge variant="info">{item.play_count} ▶</Badge>
                  </li>
                ))}
              </ol>
            )}
          </CardContent>
        </Card>
      </div>

      <p className="text-right text-xs text-muted-foreground">
        Yangilangan: {new Date(stats.generated_at).toLocaleString("uz")}
      </p>
    </div>
  );
}
