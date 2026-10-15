# Android Build

Requires Flutter + Android SDK on the build machine (not present in the packaging environment).

```powershell
cd mobile
flutter pub get
flutter doctor
flutter build apk --debug
flutter build apk --release --dart-define=API_BASE_URL=https://your-api.example.com
flutter build appbundle --release --dart-define=API_BASE_URL=https://your-api.example.com
```

Configure signing in `android/app/build.gradle` and `key.properties` (never commit the keystore).
