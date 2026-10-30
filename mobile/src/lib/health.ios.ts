import {
  CategoryValueSleepAnalysis,
  isHealthDataAvailable,
  queryCategorySamples,
  queryQuantitySamples,
  queryStatisticsForQuantity,
  requestAuthorization,
} from '@kingstinct/react-native-healthkit';
import {finite, localDateISO, unionHours, WearableSnapshot} from './health.types';

const READ_TYPES = [
  'HKQuantityTypeIdentifierStepCount',
  'HKCategoryTypeIdentifierSleepAnalysis',
  'HKQuantityTypeIdentifierRestingHeartRate',
  'HKQuantityTypeIdentifierHeartRateVariabilitySDNN',
  'HKQuantityTypeIdentifierActiveEnergyBurned',
] as const;

const latestQuantity = (rows: Array<{quantity?: number; startDate?: Date; endDate?: Date}>) => {
  const clean = rows.filter(row => Number.isFinite(Number(row?.quantity)));
  clean.sort((a, b) => {
    const aDate = a.endDate ?? a.startDate ?? new Date(0);
    const bDate = b.endDate ?? b.startDate ?? new Date(0);
    return aDate.getTime() - bDate.getTime();
  });
  return finite(clean.at(-1)?.quantity);
};

export async function readHealthSnapshot(): Promise<WearableSnapshot> {
  const available = await isHealthDataAvailable();
  if (!available) {
    throw new Error('Apple Health is unavailable on this device.');
  }

  await requestAuthorization({toRead: [...READ_TYPES]});

  const now = new Date();
  const start = new Date(now);
  start.setHours(0, 0, 0, 0);
  const sleepStart = new Date(start);
  sleepStart.setDate(sleepStart.getDate() - 1);
  sleepStart.setHours(12, 0, 0, 0);

  const todayFilter = {date: {startDate: start, endDate: now}};
  const [stepStats, sleep, resting, hrv, activeStats] = await Promise.all([
    queryStatisticsForQuantity(
      'HKQuantityTypeIdentifierStepCount',
      ['cumulativeSum'],
      {filter: todayFilter, unit: 'count'},
    ),
    queryCategorySamples('HKCategoryTypeIdentifierSleepAnalysis', {
      limit: 0,
      ascending: true,
      filter: {date: {startDate: sleepStart, endDate: now}},
    }),
    queryQuantitySamples('HKQuantityTypeIdentifierRestingHeartRate', {
      limit: 20,
      ascending: true,
      unit: 'count/min',
      filter: todayFilter,
    }),
    queryQuantitySamples('HKQuantityTypeIdentifierHeartRateVariabilitySDNN', {
      limit: 20,
      ascending: true,
      unit: 'ms',
      filter: todayFilter,
    }),
    queryStatisticsForQuantity(
      'HKQuantityTypeIdentifierActiveEnergyBurned',
      ['cumulativeSum'],
      {filter: todayFilter, unit: 'kcal'},
    ),
  ]);

  const asleepValues = new Set<number>([
    CategoryValueSleepAnalysis.asleepUnspecified,
    CategoryValueSleepAnalysis.asleepCore,
    CategoryValueSleepAnalysis.asleepDeep,
    CategoryValueSleepAnalysis.asleepREM,
  ]);
  const asleep = sleep.filter(row => asleepValues.has(Number(row.value)));
  const sleepHours = unionHours(
    asleep.map(row => ({start: row.startDate.toISOString(), end: row.endDate.toISOString()})),
  );

  return {
    metric_date: localDateISO(now),
    source: 'Apple Health',
    sleep_hours: Number(sleepHours.toFixed(2)),
    sleep_quality: 5,
    steps: Math.max(0, Math.round(finite(stepStats.sumQuantity?.quantity))),
    resting_hr: Number(latestQuantity(resting).toFixed(1)),
    hrv_ms: Number(latestQuantity(hrv).toFixed(1)),
    active_calories: Number(finite(activeStats.sumQuantity?.quantity).toFixed(1)),
    notes: 'Foreground mobile sync from Apple Health. HRV source metric: SDNN.',
  };
}
