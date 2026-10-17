import 'package:flutter/material.dart';
import '../../theme/mega_theme.dart';

/// Developer splash — "Engineered by BAM Studio"
/// Displays for exactly 5 seconds, then navigates to login.
/// Separate from Mega Hotel branding.
class DeveloperSplash extends StatefulWidget {
  const DeveloperSplash({super.key});

  @override
  State<DeveloperSplash> createState() => _DeveloperSplashState();
}

class _DeveloperSplashState extends State<DeveloperSplash>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fade;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fade = CurvedAnimation(parent: _controller, curve: Curves.easeIn);
    _controller.forward();

    Future.delayed(const Duration(seconds: 5), () {
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/login');
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1F14),
      body: FadeTransition(
        opacity: _fade,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Engineered by',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.7),
                  fontSize: 14,
                  letterSpacing: 2,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'BAM Studio',
                style: TextStyle(
                  color: MegaTheme.gold,
                  fontSize: 28,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
