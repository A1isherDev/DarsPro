"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge, Card, CardContent, type BadgeVariant } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/ui/dialog";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingScreen } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";
import { apiError } from "@/lib/api";
import { deleteItem, fetchMyItems, fetchPage } from "@/lib/content";
import { LoadMore } from "@/components/shared/LoadMore";
import { FolderOpen } from "lucide-react";
import type { ContentItemListEntry, ContentStatus } from "@/types/api";

const STATUS_VARIANT: Record<ContentStatus, BadgeVariant> = {
  draft: "neutral",
  pending: "warning",
  published: "success",
  rejected: "destructive",
};
const STATUS_LABEL: Record<ContentStatus, string> = {
  draft: "Qoralama",
  pending: "Ko'rib chiqilmoqda",
  published: "Chop etilgan",
  rejected: "Rad etilgan",
};

export default function MyContentPage() {
  const router = useRouter();
  const toast = useToast();
  const [items, setItems] = useState<ContentItemListEntry[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toDelete, setToDelete] = useState<ContentItemListEntry | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await fetchMyItems();
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

  async function confirmDelete() {
    if (!toDelete) return;
    const id = toDelete.id;
    setToDelete(null);
    try {
      await deleteItem(id);
      setItems((list) => list.filter((i) => i.id !== id));
      toast.success("Kontent o'chirildi.");
    } catch (e) {
      toast.error(apiError(e));
    }
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold">Mening kontentim</h1>
          <p className="text-muted-foreground">
            Siz yaratgan o'yinlar va ularning holati.
          </p>
        </div>
        <Button onClick={() => router.push("/builder")}>+ Yangi</Button>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {loading ? (
        <LoadingScreen />
      ) : items.length === 0 ? (
        <EmptyState
          icon={FolderOpen}
          title="Hali kontent yaratmagansiz"
          description="Birinchi o'yiningizni yarating — u shu yerda ko'rinadi."
          action={
            <Button onClick={() => router.push("/builder")}>O'yin yaratish</Button>
          }
        />
      ) : (
        <div className="space-y-3">
          {items.map((item) => {
            return (
              <Card key={item.id}>
                <CardContent className="flex items-center justify-between gap-4 pt-5">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="truncate font-semibold">{item.title}</h3>
                      <Badge variant="primary">{item.engine_slug}</Badge>
                    </div>
                    <Badge variant={STATUS_VARIANT[item.status]} className="mt-1">
                      {STATUS_LABEL[item.status]}
                    </Badge>
                  </div>
                  <div className="flex shrink-0 gap-2">
                    {item.status === "published" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push(`/solo/${item.id}`)}
                      >
                        O'ynash
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push(`/builder?edit=${item.id}`)}
                    >
                      <Pencil size={14} /> Tahrir
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => setToDelete(item)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
          <LoadMore next={next} onLoad={loadMore} loading={loadingMore} />
        </div>
      )}

      <ConfirmDialog
        open={!!toDelete}
        title="Kontentni o'chirish"
        description={`"${toDelete?.title ?? ""}" o'chiriladi. Bu amalni qaytarib bo'lmaydi.`}
        confirmLabel="O'chirish"
        destructive
        onConfirm={confirmDelete}
        onCancel={() => setToDelete(null)}
      />
    </div>
  );
}
