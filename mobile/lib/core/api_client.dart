import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:5000',
  );

  String? _token;

  void setToken(String? token) => _token = token;

  Map<String, String> get _headers {
    final h = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_token != null) h['Authorization'] = 'Bearer $_token';
    return h;
  }

  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, dynamic>? body,
    String? idempotencyKey,
  }) async {
    final headers = Map<String, String>.from(_headers);
    if (idempotencyKey != null) {
      headers['X-Idempotency-Key'] = idempotencyKey;
    }
    final res = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: headers,
      body: body == null ? null : jsonEncode(body),
    ).timeout(const Duration(seconds: 30));
    return _handle(res);
  }

  Future<Map<String, dynamic>> get(String path) async {
    final res = await http.get(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
    ).timeout(const Duration(seconds: 25));
    return _handle(res);
  }

  Future<Map<String, dynamic>> patch(
    String path, {
    Map<String, dynamic>? body,
  }) async {
    final res = await http.patch(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
      body: body == null ? null : jsonEncode(body),
    ).timeout(const Duration(seconds: 30));
    return _handle(res);
  }

  Map<String, dynamic> _handle(http.Response res) {
    Map<String, dynamic> data = {};
    try {
      final decoded = jsonDecode(res.body.isEmpty ? '{}' : res.body);
      if (decoded is Map<String, dynamic>) data = decoded;
    } on FormatException {
      // Non-JSON responses can occur when a proxy or server fails.
    }

    if (res.statusCode >= 400) {
      final message = data['message'];
      throw ApiException(
        statusCode: res.statusCode,
        message: message is String && message.isNotEmpty
            ? message
            : 'Request failed (HTTP ${res.statusCode}). Please try again.',
        error: data['error'] is String ? data['error'] as String : null,
      );
    }

    return data;
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  final String? error;

  ApiException({
    required this.statusCode,
    required this.message,
    this.error,
  });

  @override
  String toString() => message;
}
