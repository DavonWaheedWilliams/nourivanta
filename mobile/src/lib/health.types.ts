export type WearableSnapshot = {
  metric_date: string;
  source: 'Apple Health' | 'Health Connect';
  sleep_hours: number;
  sleep_quality: number;
  steps: number;
  resting_hr: number;
  hrv_ms: number;
  active_calories: number;
  notes: string;
};

export type WearableRecord = WearableSnapshot & {id: number};

export const localDateISO = (value = new Date()) => {
  const y = value.getFullYear();
  const m = String(value.getMonth() + 1).padStart(2, '0');
  const d = String(value.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

export const finite = (value: unknown, fallback = 0) => {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
};

export function unionHours(intervals: Array<{start: string; end: string}>): number {
  const ranges = intervals
    .map(({start, end}) => [new Date(start).getTime(), new Date(end).getTime()] as const)
    .filter(([start, end]) => Number.isFinite(start) && Number.isFinite(end) && end > start)
    .sort((a, b) => a[0] - b[0]);
  if (!ranges.length) return 0;
  let total = 0;
  let [start, end] = ranges[0];
  for (const [nextStart, nextEnd] of ranges.slice(1)) {
    if (nextStart <= end) end = Math.max(end, nextEnd);
    else { total += end - start; start = nextStart; end = nextEnd; }
  }
  total += end - start;
  return Math.min(24, Math.max(0, total / 3_600_000));
}
