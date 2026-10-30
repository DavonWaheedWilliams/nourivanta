# NouriVanta mobile production status

## Implemented in code

- Expo SDK 58 / React Native 0.88 mobile foundation
- FastAPI mobile backend using the shared NouriVanta database
- Secure bearer-token login and device SecureStore
- Apple Health foreground permission + read integration using `@kingstinct/react-native-healthkit` 16.x
- Android Health Connect foreground permission + read integration using `react-native-health-connect` 4.1.x
- Shared wearable upsert endpoint for steps, sleep, resting heart rate, HRV and active calories
- Android daily source reconciliation prevents cross-app step and active-calorie double counting
- Database-backed API readiness endpoint
- API pytest suite
- GitHub Actions API tests and mobile TypeScript/Expo checks
- Docker API deployment definition
- EAS development, preview and production profiles
- Expo SDK 58 Android compile SDK 37 / target SDK 36 and iOS 16.4+ deployment target

## External release work still required

- Deploy the FastAPI container to an HTTPS host and set `DATABASE_URL`, `NOURIVANTA_JWT_SECRET`, and production CORS settings
- Set `EXPO_PUBLIC_API_URL` to the production API URL before signed builds
- Run `npm install` and commit the generated `mobile/package-lock.json`
- Link the Expo/EAS project and create signed iOS/Android development builds
- Verify Apple Health on a physical iPhone and Health Connect on physical Android devices
- Complete Google Play Health Connect data-access declaration
- Complete Apple App Privacy and Google Play Data Safety forms
- Add final app icon/splash/support/privacy-policy URLs and store screenshots
- Complete TestFlight and Google Play closed testing before production submission

## Deferred on purpose

Background health sync, Garmin/Fitbit OAuth, push notifications, offline queues, passkeys, and additional features are outside this production-stability milestone.
