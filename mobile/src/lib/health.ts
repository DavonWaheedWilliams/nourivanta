import {WearableSnapshot} from './health.types';

export async function readHealthSnapshot(): Promise<WearableSnapshot> {
  throw new Error('Wearable sync requires the signed iOS or Android development build.');
}
