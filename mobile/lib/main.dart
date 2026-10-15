import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'theme/mega_theme.dart';
import 'core/api_client.dart';
import 'core/auth_state.dart';
import 'core/locale_state.dart';
import 'features/splash/developer_splash.dart';
import 'features/auth/login_screen.dart';
import 'features/home/home_screen.dart';
import 'features/admin/admin_dashboard.dart';
import 'features/staff/staff_dashboard.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  runApp(const MegaHotelApp());
}

class MegaHotelApp extends StatelessWidget {
  const MegaHotelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthState()),
        ChangeNotifierProvider(create: (_) => LocaleState()),
        Provider(create: (_) => ApiClient()),
      ],
      child: Consumer<LocaleState>(
        builder: (context, localeState, _) {
          return MaterialApp(
            title: 'Mega Hotel',
            debugShowCheckedModeBanner: false,
            theme: MegaTheme.light,
            locale: localeState.locale,
            supportedLocales: const [
              Locale('en'),
              Locale('ne'),
            ],
            localizationsDelegates: const [
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            home: const DeveloperSplash(),
            routes: {
              '/login': (_) => const LoginScreen(),
              '/home': (_) => const HomeScreen(),
              '/admin': (_) => const AdminDashboard(),
              '/staff': (_) => const StaffDashboard(),
            },
          );
        },
      ),
    );
  }
}
