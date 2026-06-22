// DarsPro — sinf rejimi WebSocket client.
//
// MUHIM: Backend Django Channels (xom WebSocket) ishlatadi, Socket.IO EMAS.
// Shuning uchun bu yerda brauzerning native WebSocket API'si ishlatiladi.

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

// Server -> Client eventlar (consumers/session_consumer.py bilan mos)
export type ServerEvent =
  | { type: "player_joined"; participant_id: string; display_name: string; total_players: number }
  | { type: "game_started"; content_data: unknown; settings: unknown }
  | { type: "question_show"; index: number; question: Record<string, unknown>; time_limit: number }
  | { type: "answer_result"; correct: boolean; score_delta: number }
  | { type: "leaderboard_update"; rankings: Array<{ name: string; score: number; team: number | null }> }
  | { type: "game_paused" }
  | { type: "game_ended"; final_results: Array<{ name: string; score: number; team: number | null }> }
  | { type: "error"; detail: string };

// Client -> Server eventlar
export type ClientEvent =
  | { type: "player_join"; display_name: string; team_number?: number | null }
  | { type: "answer_submit"; question_index: number; answer: unknown; time_taken: number }
  | { type: "host_next" }
  | { type: "host_pause" }
  | { type: "host_end" };

export interface SessionSocketHandlers {
  onMessage: (event: ServerEvent) => void;
  /** Har ulanish (shu jumladan reconnect) ochilganda chaqiriladi —
   *  o'quvchi shu yerda player_join'ni qayta yuboradi (consumer idempotent). */
  onOpen?: () => void;
  onClose?: (code: number) => void;
  /** Reconnect urinishlari boshlanganda/tugaganda holatni bildiradi. */
  onReconnecting?: (attempt: number) => void;
}

// 4404 (sessiya topilmadi) va 1000 (oddiy yopilish) reconnect qilinmaydi
const NO_RETRY_CODES = new Set([1000, 4404]);
const MAX_RETRIES = 6;

export class SessionSocket {
  private ws: WebSocket | null = null;
  private manualClose = false;
  private retries = 0;
  private retryTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private joinCode: string,
    private handlers: SessionSocketHandlers,
    private token?: string | null
  ) {}

  connect() {
    const q = this.token ? `?token=${encodeURIComponent(this.token)}` : "";
    this.ws = new WebSocket(`${WS_URL}/ws/session/${this.joinCode}/${q}`);
    this.ws.onopen = () => {
      this.retries = 0;
      this.handlers.onOpen?.();
    };
    this.ws.onclose = (e) => {
      this.handlers.onClose?.(e.code);
      if (
        !this.manualClose &&
        !NO_RETRY_CODES.has(e.code) &&
        this.retries < MAX_RETRIES
      ) {
        this.scheduleReconnect();
      }
    };
    this.ws.onmessage = (e) => {
      try {
        this.handlers.onMessage(JSON.parse(e.data) as ServerEvent);
      } catch {
        /* yaroqsiz xabar — e'tiborsiz */
      }
    };
  }

  private scheduleReconnect() {
    this.retries += 1;
    // Eksponensial backoff: 1s, 2s, 4s … maksimal 10s
    const delay = Math.min(1000 * 2 ** (this.retries - 1), 10000);
    this.handlers.onReconnecting?.(this.retries);
    this.retryTimer = setTimeout(() => this.connect(), delay);
  }

  send(event: ClientEvent) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(event));
    }
  }

  close() {
    this.manualClose = true;
    if (this.retryTimer) clearTimeout(this.retryTimer);
    this.ws?.close();
    this.ws = null;
  }
}
