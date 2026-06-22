// DarsPro — yengil ovoz effektlari (Web Audio API, audio fayl yo'q).
// Mute holati localStorage'da saqlanadi.

type SoundType = "correct" | "wrong" | "win" | "tick";

const MUTE_KEY = "darspro_muted";

export function isMuted(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(MUTE_KEY) === "1";
}

export function setMuted(muted: boolean) {
  localStorage.setItem(MUTE_KEY, muted ? "1" : "0");
}

let ctx: AudioContext | null = null;
function audioCtx(): AudioContext | null {
  if (typeof window === "undefined") return null;
  if (!ctx) {
    const AC = window.AudioContext || (window as any).webkitAudioContext;
    if (!AC) return null;
    ctx = new AC();
  }
  return ctx;
}

function tone(freq: number, start: number, dur: number, type: OscillatorType = "sine") {
  const ac = audioCtx();
  if (!ac) return;
  const osc = ac.createOscillator();
  const gain = ac.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  osc.connect(gain);
  gain.connect(ac.destination);
  const t = ac.currentTime + start;
  gain.gain.setValueAtTime(0.0001, t);
  gain.gain.exponentialRampToValueAtTime(0.18, t + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  osc.start(t);
  osc.stop(t + dur);
}

export function playSound(type: SoundType) {
  if (isMuted()) return;
  const ac = audioCtx();
  if (!ac) return;
  if (ac.state === "suspended") ac.resume();
  switch (type) {
    case "correct":
      tone(660, 0, 0.15);
      tone(880, 0.12, 0.2);
      break;
    case "wrong":
      tone(200, 0, 0.3, "sawtooth");
      break;
    case "win":
      [523, 659, 784, 1047].forEach((f, i) => tone(f, i * 0.12, 0.25));
      break;
    case "tick":
      tone(440, 0, 0.05, "square");
      break;
  }
}
