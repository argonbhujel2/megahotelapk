import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/auth_state.dart';
import '../../core/api_client.dart';
import '../../theme/mega_theme.dart';

class StaffDashboard extends StatefulWidget {
  const StaffDashboard({super.key});

  @override
  State<StaffDashboard> createState() => _StaffDashboardState();
}

class _StaffDashboardState extends State<StaffDashboard> {
  List<dynamic> _orders = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final api = context.read<ApiClient>();
      final res = await api.get('/api/v1/staff/assigned-orders');
      setState(() => _orders = res['orders'] as List? ?? []);
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Staff'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await context.read<AuthState>().logout();
              if (mounted) Navigator.of(context).pushReplacementNamed('/login');
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _orders.isEmpty
              ? const Center(child: Text('No assigned deliveries'))
              : ListView.builder(
                  itemCount: _orders.length,
                  itemBuilder: (_, i) {
                    final o = _orders[i];
                    return Card(
                      child: ListTile(
                        title: Text(o['order_number'] ?? ''),
                        subtitle: Text('Status: ${o['status']} • NPR ${o['total']}'),
                        trailing: o['payment_method'] == 'cod'
                            ? TextButton(
                                onPressed: () => _collectCod(o['id']),
                                child: const Text('Collect COD'),
                              )
                            : null,
                      ),
                    );
                  },
                ),
    );
  }

  Future<void> _collectCod(String orderId) async {
    try {
      final api = context.read<ApiClient>();
      await api.post('/api/v1/staff/cod-collect/$orderId');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('COD marked collected')),
        );
        _load();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$e')),
        );
      }
    }
  }
}
