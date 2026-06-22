"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Badge, Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";
import { PLAN_LABELS } from "@/lib/utils";
import { useAuth } from "@/lib/store";

export default function ProfilePage() {
  const { user, loading, updateProfile } = useAuth();
  const toast = useToast();
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");

  useEffect(() => {
    if (user) {
      setFullName(user.full_name ?? "");
      setPhone(user.phone ?? "");
    }
  }, [user]);

  if (!user) return null;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await updateProfile({ full_name: fullName, phone: phone || null });
      toast.success("Profil saqlandi.");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Xatolik");
    }
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold">Profil</h1>
        <p className="text-muted-foreground">Shaxsiy ma'lumotlaringiz va tarifingiz.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Tarif</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center gap-3">
          <Badge>{PLAN_LABELS[user.effective_plan]}</Badge>
          {user.plan_expires_at ? (
            <span className="text-sm text-muted-foreground">
              {new Date(user.plan_expires_at).toLocaleDateString("uz")} gacha
            </span>
          ) : (
            <span className="text-sm text-muted-foreground">Muddatsiz (bepul)</span>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Ma'lumotlar</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" value={user.email} disabled />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="full_name">To'liq ism</Label>
              <Input
                id="full_name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Familiya Ism"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="phone">Telefon</Label>
              <Input
                id="phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+998 90 123 45 67"
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading && <Spinner size={16} />}
              {loading ? "Saqlanmoqda…" : "Saqlash"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
