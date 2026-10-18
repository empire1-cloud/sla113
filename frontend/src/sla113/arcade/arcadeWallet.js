/**
 * Southern Lifestyle Arcade wallet — one shared cacao balance across every cabinet.
 * Virtual play credits only: no cash value, no purchase, no redemption.
 * Lives in localStorage until an authoritative backend owns the economy.
 */

const KEY = 'aztlan_arcade_cacao_v1';
export const STARTING_CACAO = 2500;
export const REFILL_FLOOR = 100;

const listeners = new Set();

function read() {
  try {
    const raw = window.localStorage.getItem(KEY);
    const n = raw === null ? STARTING_CACAO : Number(raw);
    return Number.isFinite(n) && n >= 0 ? Math.floor(n) : STARTING_CACAO;
  } catch {
    return STARTING_CACAO;
  }
}

let balance = typeof window === 'undefined' ? STARTING_CACAO : read();

function write(next) {
  balance = Math.max(0, Math.floor(next));
  try { window.localStorage.setItem(KEY, String(balance)); } catch { /* private mode */ }
  listeners.forEach((fn) => fn(balance));
  return balance;
}

export const getCacao = () => balance;
export const setCacao = (n) => write(n);
export const addCacao = (n) => write(balance + n);

/** Returns true and debits when affordable; false (no change) otherwise. */
export function spendCacao(n) {
  if (n > balance) return false;
  write(balance - n);
  return true;
}

/** Free demo top-up, only when the player is nearly out. */
export function refillCacao() {
  if (balance >= REFILL_FLOOR) return false;
  write(STARTING_CACAO);
  return true;
}

export function subscribeCacao(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}
