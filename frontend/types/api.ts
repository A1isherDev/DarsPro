// DarsPro — backend API response interfacelari (CLAUDE.md "types/api.ts" qoidasi)

export type Plan = "free" | "start" | "pro" | "max";
export type ContentStatus = "draft" | "pending" | "published" | "rejected";
export type ContentSource = "staff" | "teacher";
export type SessionMode = "solo" | "class" | "pair" | "team";
export type SessionStatus = "waiting" | "active" | "ended";

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  telegram_id: string | null;
  auth_provider: string;
  plan: Plan;
  effective_plan: Plan;
  plan_expires_at: string | null;
  is_staff: boolean;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface RegisterResponse {
  user: User;
  tokens: AuthTokens;
}

export interface Grade {
  id: number;
  number: number;
  label: string;
}

export interface Subject {
  id: string;
  name: string;
  slug: string;
  icon: string;
  is_active: boolean;
}

export interface Topic {
  id: string;
  subject: string;
  grade: number;
  title: string;
  slug: string;
  order: number;
  is_active: boolean;
}

export interface GameEngine {
  id: string;
  name: string;
  slug: EngineSlug;
  default_config: Record<string, unknown>;
}

export interface ContentItemListEntry {
  id: string;
  title: string;
  topic: string;
  engine: string;
  engine_slug: EngineSlug;
  source: ContentSource;
  status: ContentStatus;
  play_count: number;
  is_favorited?: boolean;
  created_at: string;
}

export interface ContentItemDetail<T = unknown> extends ContentItemListEntry {
  created_by: string | null;
  data: T;
}

export interface GameSession {
  id: string;
  content: string;
  content_title: string;
  engine_slug: EngineSlug;
  join_code: string;
  mode: SessionMode;
  status: SessionStatus;
  max_players: number;
  settings: Record<string, unknown>;
  participant_count: number;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
}

export interface Participant {
  id: string;
  display_name: string;
  team_number: number | null;
  score: number;
  joined_at: string;
}

export interface SessionResults {
  session_id: string;
  join_code: string;
  status: SessionStatus;
  total_players: number;
  rankings: Array<{
    rank: number;
    display_name: string;
    team_number: number | null;
    score: number;
  }>;
}

export interface UserStats {
  total_games: number;
  total_score: number;
  avg_score: number;
  best_score: number;
  total_seconds: number;
}

export interface UserGameHistory {
  id: string;
  content: string;
  content_title: string;
  engine_slug: EngineSlug;
  score: number;
  duration_sec: number;
  played_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// types/engines.ts dan
import type { EngineSlug } from "./engines";
