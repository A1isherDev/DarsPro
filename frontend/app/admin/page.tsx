"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Badge, Card, CardContent } from "@/components/ui/card";
import { api, apiError } from "@/lib/api";
import { fetchPage } from "@/lib/content";
import { LoadMore } from "@/components/shared/LoadMore";
import { useToast } from "@/components/ui/toast";
import type { ContentItemListEntry, Paginated } from "@/types/api";

export default function AdminReviewPage() {
  const [items, setItems] = useState<ContentItemListEntry[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const toast = useToast();

  async function load() {
    setLoading(true);
    try {
      const { data } = await api.get<Paginated<ContentItemListEntry>>(
        "/admin/items/pending"
      );
      setItems(data.results);
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
      const data = await fetchPage<ContentItemListEntry>(next);
      setItems((prev) => [...prev, ...data.results]);
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

  async function decide(id: string, action: "approve" | "reject") {
    setBusy(id);
    setError(null);
    try {
      await api.patch(`/admin/items/${id}/${action}`);
      setItems((list) => list.filter((i) => i.id !== id));
      toast.success(action === "approve" ? "Tasdiqlandi." : "Rad etildi.");
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold">Review navbati</h1>
        <p className="text-muted-foreground">
          O'qituvchilar yuborgan kontentni ko'rib chiqing.
        </p>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {loading ? (
        <p className="text-muted-foreground">Yuklanmoqda…</p>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            Navbat bo'sh — barcha kontent ko'rib chiqilgan. ✅
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <Card key={item.id}>
              <CardContent className="flex items-center justify-between gap-4 pt-5">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="truncate font-semibold">{item.title}</h3>
                    <Badge>{item.engine_slug}</Badge>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Yuborilgan:{" "}
                    {new Date(item.created_at).toLocaleString("uz")}
                  </p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <Link href={`/solo/${item.id}`} target="_blank">
                    <Button variant="outline" size="sm">
                      Ko'rish
                    </Button>
                  </Link>
                  <Button
                    size="sm"
                    disabled={busy === item.id}
                    onClick={() => decide(item.id, "approve")}
                  >
                    Tasdiqlash
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    disabled={busy === item.id}
                    onClick={() => decide(item.id, "reject")}
                  >
                    Rad etish
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
          <LoadMore next={next} onLoad={loadMore} loading={loadingMore} />
        </div>
      )}
    </div>
  );
}
