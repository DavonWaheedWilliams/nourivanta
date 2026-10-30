import {initialize, readRecords, requestPermission} from 'react-native-health-connect';
import {finite, localDateISO, unionHours, WearableSnapshot} from './health.types';

const rows = (value: any): any[] => value?.records || value?.result || [];
const maxTotalByOrigin = (items: any[], valueOf: (item: any) => number) => {
  const totals = new Map<string, number>();
  for (const item of items) {
    const origin = String(item?.metadata?.dataOrigin || 'unknown');
    totals.set(origin, (totals.get(origin) || 0) + Math.max(0, finite(valueOf(item))));
  }
  return Math.max(0, ...totals.values());
};

const latest = (items: any[], field: string) => {
  const clean = items.filter(item => Number.isFinite(Number(item?.[field])));
  clean.sort((a, b) => new Date(a.time || a.endTime || a.startTime || 0).getTime() - new Date(b.time || b.endTime || b.startTime || 0).getTime());
  return finite(clean.at(-1)?.[field]);
};

export async function readHealthSnapshot(): Promise<WearableSnapshot> {
  const ready = await initialize();
  if (!ready) throw new Error('Health Connect is unavailable on this device.');

  await requestPermission([
    {accessType: 'read', recordType: 'Steps'},
    {accessType: 'read', recordType: 'SleepSession'},
    {accessType: 'read', recordType: 'RestingHeartRate'},
    {accessType: 'read', recordType: 'HeartRateVariabilityRmssd'},
    {accessType: 'read', recordType: 'ActiveCaloriesBurned'},
  ] as any);

  const now = new Date();
  const start = new Date(now); start.setHours(0, 0, 0, 0);
  const sleepStart = new Date(start); sleepStart.setDate(sleepStart.getDate() - 1); sleepStart.setHours(12, 0, 0, 0);
  const dayFilter = {timeRangeFilter: {operator: 'between' as const, startTime: start.toISOString(), endTime: now.toISOString()}};
  const sleepFilter = {timeRangeFilter: {operator: 'between' as const, startTime: sleepStart.toISOString(), endTime: now.toISOString()}};

  const [stepResult, sleepResult, restResult, hrvResult, activeResult] = await Promise.all([
    readRecords('Steps', dayFilter as any),
    readRecords('SleepSession', sleepFilter as any),
    readRecords('RestingHeartRate', dayFilter as any),
    readRecords('HeartRateVariabilityRmssd', dayFilter as any),
    readRecords('ActiveCaloriesBurned', dayFilter as any),
  ]);

  const stepRows = rows(stepResult);
  const sleepRows = rows(sleepResult);
  const restRows = rows(restResult);
  const hrvRows = rows(hrvResult);
  const activeRows = rows(activeResult);

  const steps = maxTotalByOrigin(stepRows, row => row?.count);
  const sleepHours = unionHours(sleepRows.map(row => ({start: row.startTime, end: row.endTime})));
  const activeCalories = maxTotalByOrigin(activeRows, row => row?.energy?.inKilocalories);

  return {
    metric_date: localDateISO(now),
    source: 'Health Connect',
    sleep_hours: Number(sleepHours.toFixed(2)),
    sleep_quality: 5,
    steps: Math.round(steps),
    resting_hr: Number(latest(restRows, 'beatsPerMinute').toFixed(1)),
    hrv_ms: Number(latest(hrvRows, 'heartRateVariabilityMillis').toFixed(1)),
    active_calories: Number(activeCalories.toFixed(1)),
    notes: 'Foreground mobile sync from Android Health Connect. HRV source metric: RMSSD. Daily steps and active calories use the highest contributing data origin to avoid cross-source double counting.',
  };
}
