import 'dart:convert';
import 'package:http/http.dart' as http;

/// Central API client. Base URL must be configured per environment.
/// Never embed production secrets here.
class ApiClient {
  // Override via --dart-define=API_BASE_URL=https://... for release builds
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:5000', // Android emulator → host
  );

  String? _token;

  void setToken(String? token) => _token = token;

  Map<String, String> get _headers {
    final h = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_token != null) h['Authorization'] = 'Bearer $_token';
    return h;
  }

  Future<Map<String, dynamic>> post(String path, {Map<String, dynamic>? body, String? idempotencyKey}) async {
    final headers = Map<String, String>.from(_headers);
    if (idempotencyKey != null) headers['X-Idempotency-Key'] = idempotencyKey;
    final res = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: headers,
      body: body != null ? jsonEncode(body) : null,
    );
    return _handle(res);
  }

  Future<Map<String, dynamic>> get(String path) async {
    final res = await http.get(Uri.parse('$baseUrl$path'), headers: _headers);
    return _handle(res);
  }

  Future<Map<String, dynamic>> patch(String path, {Map<String, dynamic>? body}) async {
    final res = await http.patch(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
      body: body != null ? jsonEncode(body) : null,
    );
    return _handle(res);
  }

  Map<String, dynamic> _handle(http.Response res) {
    final data = jsonDecode(res.body.isEmpty ? '{}' : res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      throw ApiException(
        statusCode: res.statusCode,
        message: data['message'] as String? ?? 'Request failed',
        error: data['error'] as String?,
      );
    }
    return data;
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  final String? error;
  ApiException({required this.statusCode, required this.message, this.error});
  @override
  String toString() => message;
}
