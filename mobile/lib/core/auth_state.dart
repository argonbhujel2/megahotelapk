import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthState extends ChangeNotifier {
  final _storage = const FlutterSecureStorage();
  String? _accessToken;
  String? _role;
  String? _userId;
  bool _isGuest = false;
  bool _initialized = false;

  bool get isAuthenticated => _accessToken != null;
  bool get isGuest => _isGuest;
  String? get role => _role;
  String? get userId => _userId;
  String? get accessToken => _accessToken;
  bool get initialized => _initialized;

  Future<void> init() async {
    _accessToken = await _storage.read(key: 'access_token');
    _role = await _storage.read(key: 'role');
    _userId = await _storage.read(key: 'user_id');
    _initialized = true;
    notifyListeners();
  }

  Future<void> setSession({
    required String accessToken,
    required String role,
    required String userId,
  }) async {
    _accessToken = accessToken;
    _role = role;
    _userId = userId;
    _isGuest = false;
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'role', value: role);
    await _storage.write(key: 'user_id', value: userId);
    notifyListeners();
  }

  void setGuest() {
    _isGuest = true;
    _accessToken = null;
    _role = null;
    _userId = null;
    notifyListeners();
  }

  Future<void> logout() async {
    _accessToken = null;
    _role = null;
    _userId = null;
    _isGuest = false;
    await _storage.deleteAll();
    notifyListeners();
  }

  /// Route after successful auth — never trust client role for authorization.
  String homeRouteForRole() {
    switch (_role) {
      case 'admin':
        return '/admin';
      case 'staff':
        return '/staff';
      default:
        return '/home';
    }
  }
}
