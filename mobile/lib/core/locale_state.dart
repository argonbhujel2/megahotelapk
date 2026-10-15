import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LocaleState extends ChangeNotifier {
  Locale _locale = const Locale('en');
  Locale get locale => _locale;
  bool get isNepali => _locale.languageCode == 'ne';

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final code = prefs.getString('language') ?? 'en';
    _locale = Locale(code);
    notifyListeners();
  }

  Future<void> setLocale(String code) async {
    _locale = Locale(code);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('language', code);
    notifyListeners();
  }
}
