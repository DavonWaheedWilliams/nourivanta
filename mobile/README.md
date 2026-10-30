# NouriVanta Mobile 1.1

Native Expo/React Native client for the existing NouriVanta account and PostgreSQL database. The mobile app uses the same core data as the Streamlit web app.

## Production focus in this release

- Expo SDK 58 / React Native 0.88
- Secure sign-in and SecureStore token storage
- Native iOS Apple Health foreground sync
- Native Android Health Connect foreground sync
- Steps, sleep, resting heart rate, HRV and active calories
- Wearable data saved through the shared `wearable_metrics` table
- Native barcode camera, dashboard, nutrition, workouts, readiness, progress and account deletion
- EAS development, preview and production profiles

## Local setup

1. Install Node.js 22.13 or newer.
2. From `mobile`, run `npm install`.
3. Copy `.env.example` to `.env`.
4. Set `EXPO_PUBLIC_API_URL` to the HTTPS FastAPI URL.
5. Run `npx expo prebuild --clean`.
6. Create a development build. HealthKit and Health Connect do not run inside Expo Go.

```bash
npx eas-cli@latest login
npx eas-cli@latest build --profile development --platform android
npx eas-cli@latest build --profile development --platform ios
```

## Production builds

```bash
npx eas-cli@latest build --platform android --profile production
npx eas-cli@latest build --platform ios --profile production
```

Before production submission, deploy the API over HTTPS, set the mobile production API URL, complete Apple/Google health-data declarations, run physical-device tests, and complete store privacy forms.

## Health integration libraries

- iOS: `@kingstinct/react-native-healthkit` 16.x with its Expo config plugin and Nitro modules.
- Android: `react-native-health-connect` 4.1.x.
- iOS HRV is HealthKit SDNN. Android HRV is Health Connect RMSSD. The API stores both in the existing `hrv_ms` field and preserves the source in each wearable row.
- Expo SDK 58 uses Android compile SDK 37, target SDK 36 and iOS deployment target 16.4 in this project.

Health data requires a development or production build. Expo Go is not used for this integration.
