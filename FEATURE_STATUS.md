# NouriVanta Elite feature status

## Working in the Streamlit application

- Adaptive coaching reports
- USDA food search
- Open Food Facts barcode lookup
- Food-photo macro estimates
- Nutrition-label photo scanning
- Favorites, recent foods, saved meals, diary copy
- Macro Forecast and Fuel Gap Map
- Workout programs, substitutions, rest timer, overload guidance, PRs, recovery map
- Meal planning, pantry, grocery list, budget estimate
- Progress intelligence and goal forecasts
- Voice logging with editable review
- Wearable CSV import and manual metrics
- Family profiles and coach notes
- Recovery codes, lockout, session timeout, access history
- Stripe hosted payment-link display

## Working in the native mobile source

- Expo SDK 58 / React Native 0.88 application foundation
- Existing NouriVanta account and database compatibility
- Secure mobile bearer-token storage
- Dashboard, nutrition, workouts, readiness, progress, barcode scanning and account deletion
- Apple Health foreground permission/read integration using the New Architecture compatible HealthKit binding
- Android Health Connect foreground permission/read integration
- Wearable sync for steps, sleep, resting heart rate, HRV and active calories
- FastAPI wearable bridge using the existing `wearable_metrics` table
- API pytest coverage and GitHub Actions CI

## Requires external credentials or release setup

- Food-photo scanning, label scanning, voice transcription, command parsing and AI report enhancement require `OPENAI_API_KEY`.
- Full USDA quotas require `FDC_API_KEY`.
- Subscription checkout requires `STRIPE_PAYMENT_LINK`.
- Permanent Streamlit and mobile API data require the production PostgreSQL `DATABASE_URL`.
- The mobile API needs a strong `NOURIVANTA_JWT_SECRET` and HTTPS hosting.
- Apple Health and Health Connect need signed development/production builds and user permission on physical devices.

## Deferred from this production-stability milestone

- Live Garmin synchronization
- Live Fitbit synchronization
- Background health synchronization
- Background push notifications
- Offline phone entry queues
- Device passkeys

The current milestone prioritizes mobile deployment, wearable integration, automated testing and stability over additional feature expansion.
