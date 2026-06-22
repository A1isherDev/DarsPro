"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";

export default function SessionsPage() {
  const router = useRouter();
  const [code, setCode] = useState("");

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold">Sessiyalar</h1>
        <p className="text-muted-foreground">
          Sinf rejimidagi jonli o'yinlar.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Yangi sessiya</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            Sessiya kutubxonadagi o'yinda <b>"Sinf rejimi"</b> tugmasi orqali
            yaratiladi.
          </p>
          <Link href="/library">
            <Button>Kutubxonaga o'tish</Button>
          </Link>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Mavjud sessiyaga qaytish</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              const c = code.trim().toUpperCase();
              if (/^DRS-[A-Z0-9]{4}$/.test(c)) router.push(`/sessions/${c}`);
            }}
          >
            <div className="flex-1 space-y-1.5">
              <Label htmlFor="code">O'yin kodi</Label>
              <Input
                id="code"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                placeholder="DRS-XXXX"
              />
            </div>
            <Button type="submit">Ochish</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
