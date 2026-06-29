"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Check, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Badge, Card, CardContent } from "@/components/ui/card";
import { api, apiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { PlanPricing } from "@/types/api";

function formatPrice(price: number): string {
  if (price === 0) return "Bepul";
  return price.toLocaleString("uz-UZ") + " so'm";
}

export default function PricingPage() {
  const [plans, setPlans] = useState<PlanPricing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<{ plans: PlanPricing[] }>("/users/plans")
      .then(({ data }) => setPlans(data.plans))
      .catch((e) => setError(apiError(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="bg-app-gradient min-h-screen">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-block rounded-full bg-primary/12 px-4 py-1 text-sm font-semibold text-primary">
            Tariflar
          </span>
          <h1 className="mt-4 font-display text-4xl font-extrabold tracking-tight sm:text-5xl">
            O'zingizga mos rejani tanlang
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
            Bepul boshlang — kerak bo'lganda istalgan vaqtda kengaytiring. 🎮
          </p>
        </motion.div>

        {error && (
          <p className="mt-8 text-center text-sm text-destructive">{error}</p>
        )}

        {loading ? (
          <p className="mt-12 text-center text-muted-foreground">Yuklanmoqda…</p>
        ) : (
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {plans.map((plan, i) => (
              <motion.div
                key={plan.slug}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
              >
                <Card
                  className={cn(
                    "relative flex h-full flex-col",
                    plan.highlight && "ring-2 ring-primary"
                  )}
                >
                  {plan.highlight && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge variant="primary">⭐ Tavsiya etiladi</Badge>
                    </div>
                  )}
                  <CardContent className="flex flex-1 flex-col gap-5 pt-6">
                    <div>
                      <h3 className="font-display text-xl font-bold">
                        {plan.label}
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        {plan.tagline}
                      </p>
                    </div>

                    <div>
                      <span className="font-display text-3xl font-extrabold">
                        {formatPrice(plan.price)}
                      </span>
                      {plan.price > 0 && (
                        <span className="text-sm text-muted-foreground"> /oy</span>
                      )}
                    </div>

                    <ul className="flex flex-1 flex-col gap-2 text-sm">
                      {plan.features.map((f) => (
                        <li key={f} className="flex items-start gap-2">
                          <Check
                            size={16}
                            className="mt-0.5 shrink-0 text-success"
                          />
                          <span>{f}</span>
                        </li>
                      ))}
                      {plan.limits.ads && (
                        <li className="flex items-start gap-2 text-muted-foreground">
                          <X size={16} className="mt-0.5 shrink-0" />
                          <span>Reklama ko'rsatiladi</span>
                        </li>
                      )}
                    </ul>

                    <Button
                      variant={plan.highlight ? "default" : "outline"}
                      className="w-full"
                      disabled
                      title="To'lov hozircha qo'lda faollashtiriladi"
                    >
                      {plan.price === 0 ? "Hozirgi reja" : "Tez kunda"}
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        <div className="mx-auto mt-10 max-w-2xl rounded-2xl border border-border bg-card/60 p-5 text-center text-sm text-muted-foreground">
          💳 To'lov tizimi (Payme / Click) tez orada ulanadi. Hozircha pulli
          tariflar <span className="font-semibold">qo'lda faollashtiriladi</span>{" "}
          — tarif olish uchun administrator bilan bog'laning.
        </div>

        <div className="mt-8 text-center">
          <Link href="/dashboard">
            <Button variant="ghost">← Dashboardga qaytish</Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
