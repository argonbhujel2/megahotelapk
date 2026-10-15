import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Mega Hotel design system
/// Primary: Forest green
/// Background: Warm cream
/// Accent: Restrained gold
class MegaTheme {
  static const Color forestGreen = Color(0xFF1B5E3B);
  static const Color forestGreenLight = Color(0xFF2E7D4F);
  static const Color cream = Color(0xFFF8F4EC);
  static const Color creamDark = Color(0xFFEFE8DA);
  static const Color gold = Color(0xFFC9A227);
  static const Color goldSoft = Color(0xFFE8D48B);
  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF5C5C5C);
  static const Color error = Color(0xFFB3261E);
  static const Color success = Color(0xFF1B7A3D);

  static ThemeData get light {
    final base = ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.light(
        primary: forestGreen,
        onPrimary: Colors.white,
        secondary: gold,
        onSecondary: textPrimary,
        surface: cream,
        onSurface: textPrimary,
        error: error,
        background: cream,
      ),
      scaffoldBackgroundColor: cream,
      appBarTheme: AppBarTheme(
        backgroundColor: forestGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.playfairDisplay(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: forestGreen,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 16),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: creamDark),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: forestGreen, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 1,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      textTheme: TextTheme(
        displayLarge: GoogleFonts.playfairDisplay(fontSize: 32, fontWeight: FontWeight.w700, color: textPrimary),
        headlineMedium: GoogleFonts.playfairDisplay(fontSize: 22, fontWeight: FontWeight.w600, color: textPrimary),
        titleLarge: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w600, color: textPrimary),
        bodyLarge: GoogleFonts.inter(fontSize: 16, color: textPrimary),
        bodyMedium: GoogleFonts.inter(fontSize: 14, color: textSecondary),
        labelLarge: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600),
      ),
    );
    return base;
  }
}

