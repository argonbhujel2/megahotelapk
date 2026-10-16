import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/mega_theme.dart';
import '../../core/auth_state.dart';
import '../../core/api_client.dart';
import 'register_screen.dart';
import 'forgot_password_screen.dart';

/// Shared login for Customer, Admin and Staff.
/// No separate Admin login link. Role is determined by backend.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _loading = false;
  String? _error;

  void _showComingSoon(String provider) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        icon: const Icon(Icons.info_outline, size: 42),
        title: Text('$provider Login'),
        content: const Text(
          'Sorry from Mega Hotel and BAM Studio.\n\n'
          'This service will be available in the next update, '
          'version 1.0.1.1.\n\n'
          'Current version: 1.0.1.0',
          textAlign: TextAlign.center,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Future<void> _login() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final api = context.read<ApiClient>();
      final res = await api.post('/api/v1/auth/login', body: {
        'email': _emailCtrl.text.trim(),
        'password': _passwordCtrl.text,
      });
      final user = res['user'] as Map<String, dynamic>;
      final auth = context.read<AuthState>();
      await auth.setSession(
        accessToken: res['access_token'] as String,
        role: user['role'] as String,
        userId: user['id'] as String,
      );
      api.setToken(res['access_token'] as String);
      if (!mounted) return;
      Navigator.of(context).pushReplacementNamed(auth.homeRouteForRole());
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Connection error. Please try again.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _continueAsGuest() {
    context.read<AuthState>().setGuest();
    Navigator.of(context).pushReplacementNamed('/home');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              Text(
                'Mega Hotel',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.displayLarge?.copyWith(
                      color: MegaTheme.forestGreen,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Restaurant Ordering & Delivery',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 48),
              TextField(
                controller: _emailCtrl,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Icons.email_outlined),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordCtrl,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Password',
                  prefixIcon: Icon(Icons.lock_outline),
                ),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: const TextStyle(color: MegaTheme.error)),
              ],
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _loading ? null : _login,
                child: _loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('Sign In'),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const RegisterScreen(),
                    ),
                  );
                },
                child: const Text('New customer? Create account'),
              ),
              const SizedBox(height: 8),              OutlinedButton(
                onPressed: _continueAsGuest,
                style: OutlinedButton.styleFrom(
                  foregroundColor: MegaTheme.forestGreen,
                  side: const BorderSide(color: MegaTheme.forestGreen),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Continue as Guest'),
              ),
              const SizedBox(height: 24),
              const Row(
                children: [
                  Expanded(child: Divider()),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 12),
                    child: Text('OR CONTINUE WITH'),
                  ),
                  Expanded(child: Divider()),
                ],
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () => _showComingSoon('Google'),
                icon: const Icon(Icons.g_mobiledata, size: 28),
                label: const Text('Continue with Google'),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => _showComingSoon('Facebook'),
                icon: const Icon(Icons.facebook, size: 24),
                label: const Text('Continue with Facebook'),
              ),
              const SizedBox(height: 40),
              TextButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const ForgotPasswordScreen(),
                    ),
                  );
                },
                child: const Text('Forgot password?'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}



