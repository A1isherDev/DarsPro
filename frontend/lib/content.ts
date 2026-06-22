// DarsPro — kontent API yordamchilari
import { api } from "./api";
import type {
  ContentItemDetail,
  ContentItemListEntry,
  GameEngine,
  Grade,
  Paginated,
  Subject,
  Topic,
} from "@/types/api";

export async function fetchGrades(): Promise<Grade[]> {
  const { data } = await api.get<Grade[]>("/content/grades");
  return data;
}

export async function fetchSubjects(): Promise<Subject[]> {
  const { data } = await api.get<Subject[]>("/content/subjects");
  return data;
}

export async function fetchEngines(): Promise<GameEngine[]> {
  const { data } = await api.get<GameEngine[]>("/content/engines");
  return data;
}

export async function fetchTopics(params: {
  grade?: number;
  subject?: string;
}): Promise<Topic[]> {
  const { data } = await api.get<Topic[]>("/content/topics", { params });
  return data;
}

export async function fetchItems(params: {
  topic?: string;
  engine?: string;
  source?: string;
  search?: string;
}): Promise<Paginated<ContentItemListEntry>> {
  const { data } = await api.get<Paginated<ContentItemListEntry>>(
    "/content/items",
    { params }
  );
  return data;
}

// Paginatsiya: DRF qaytargan `next` (to'liq URL) bo'yicha keyingi sahifa.
// axios absolyut URL'da baseURL'ni e'tiborsiz qoldiradi.
export async function fetchPage<T>(url: string): Promise<Paginated<T>> {
  const { data } = await api.get<Paginated<T>>(url);
  return data;
}

export async function fetchItem<T = unknown>(
  id: string
): Promise<ContentItemDetail<T>> {
  const { data } = await api.get<ContentItemDetail<T>>(`/content/items/${id}`);
  return data;
}

export async function fetchMyItems(): Promise<
  Paginated<ContentItemListEntry>
> {
  const { data } = await api.get<Paginated<ContentItemListEntry>>(
    "/content/items",
    { params: { mine: "true" } }
  );
  return data;
}

export async function updateItem(
  id: string,
  payload: { title?: string; data?: unknown }
): Promise<ContentItemDetail> {
  const { data } = await api.patch<ContentItemDetail>(
    `/content/items/${id}`,
    payload
  );
  return data;
}

export async function deleteItem(id: string): Promise<void> {
  await api.delete(`/content/items/${id}`);
}

export async function setFavorite(id: string, on: boolean): Promise<void> {
  if (on) await api.post(`/content/items/${id}/favorite`);
  else await api.delete(`/content/items/${id}/favorite`);
}

export async function fetchFavorites(): Promise<
  Paginated<ContentItemListEntry>
> {
  const { data } = await api.get<Paginated<ContentItemListEntry>>(
    "/content/items/favorites"
  );
  return data;
}

export async function cloneItem(id: string): Promise<ContentItemDetail> {
  const { data } = await api.post<ContentItemDetail>(
    `/content/items/${id}/clone`
  );
  return data;
}

export async function uploadMedia(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<{ url: string }>("/content/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data.url;
}

export async function recordSoloResult(payload: {
  content: string;
  score: number;
  duration_sec: number;
}): Promise<void> {
  await api.post("/sessions/solo", payload);
}

export async function createItem(payload: {
  title: string;
  topic: string;
  engine: string;
  data: unknown;
}): Promise<ContentItemDetail> {
  const { data } = await api.post<ContentItemDetail>(
    "/content/items",
    payload
  );
  return data;
}
