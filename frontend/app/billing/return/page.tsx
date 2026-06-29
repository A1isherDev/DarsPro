"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Clock, Loader2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { User } from "@/types/api";

type State = "checking" | "active" | "pending";

export default function BillingReturnPage() {
  const [state, setState] = useState<State>("checking");
  const [plan, setPlan] = useState<string>("free");

  useEffect(() => {
    let tries = 0;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      tries += 1;
      try {
        const { data } = await api.get<User>("/users/me");
        if (data.effective_plan && data.effective_plan !== "free") {
          setPlan(data.effective_plan);
          setState("active");
          return;
        }
      } catch {
        /* davom etamiz */
      }
      if (tries >= 6) {
        setState("pending");
        return;
      }
      timer = setTimeout(poll, 2500);
    }

    poll();
    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="bg-app-gradient flex min-h-screen items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <Card className="shadow-card">
          <CardContent className="flex flex-col items-center gap-4 py-10 text-center">
            {state === "checking" && (
              <>
                <Loader2 className="animate-spin text-primary" size={40} />
                <h1 className="font-display text-xl font-bold">
                  To'lov tekshirilmoqda…
                </h1>
                <p className="text-sm text-muted-foreground">
                  Bir necha soniya kuting, tarifingizni faollashtiramiz.
                </p>
              </>
            )}
            {state === "active" && (
              <>
                <CheckCircle2 className="text-success" size={48} />
                <h1 className="font-display text-2xl font-bold">
                  Tarif faollashtirildi! 🎉
                </h1>
                <p className="text-sm text-muted-foreground">
                  Sizning rejangiz:{" "}
                  <span className="font-semibold uppercase">{plan}</span>
                </p>
                <Link href="/dashboard" className="mt-2">
                  <Button size="lg">Dashboardga o'tish</Button>
                </Link>
              </>
            )}
            {state === "pending" && (
              <>
                <Clock className="text-warning" size={44} />
                <h1 className="font-display text-xl font-bold">
                  To'lov qayta ishlanmoqda
                </h1>
                <p className="text-sm text-muted-foreground">
                  To'lovingiz tasdiqlanishi bir oz vaqt olishi mumkin. Tarif
                  avtomatik faollashadi — keyinroq profilingizni tekshiring.
                </p>
                <Link href="/dashboard" className="mt-2">
                  <Button variant="outline">Dashboardga qaytish</Button>
                </Link>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </main>
  );
}
