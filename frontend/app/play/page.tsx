"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";

export default function JoinByCodePage() {
  const router = useRouter();
  const [code, setCode] = useState("");

  function go(e: React.FormEvent) {
    e.preventDefault();
    const c = code.trim().toUpperCase();
    if (/^DRS-[A-Z0-9]{4}$/.test(c)) router.push(`/play/${c}`);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>O'yinga qo'shilish</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={go} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="code">O'yin kodi</Label>
            <Input
              id="code"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              placeholder="DRS-XXXX"
              className="text-center text-lg tracking-widest"
              autoFocus
            />
          </div>
          <Button type="submit" className="w-full">
            Kirish
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
