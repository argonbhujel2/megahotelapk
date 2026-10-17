import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/mega_theme.dart';
import '../../core/api_client.dart';
import '../../core/auth_state.dart';
import 'admin_orders_screen.dart';

class AdminDashboard extends StatefulWidget {
  const AdminDashboard({super.key});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  Map<String, dynamic>? _counts;
  List<dynamic> _slots = [];
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
      final dash = await api.get('/api/v1/admin/dashboard');
      final slots = await api.get('/api/v1/admin/delivery-slots');
      setState(() {
        _counts = dash['counts'] as Map<String, dynamic>?;
        _slots = slots['slots'] as List? ?? [];
      });
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Operations'),
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
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text('Operations', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.receipt_long),
                    title: const Text('View All Orders'),
                    subtitle: const Text('Open orders, customer details and delivery addresses'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const AdminOrdersScreen(),
                        ),
                      );
                    },
                  ),
                ),
                _StatCard(label: 'New Orders', value: '${_counts?['new'] ?? 0}', color: MegaTheme.forestGreen),
                _StatCard(label: 'Preparing', value: '${_counts?['preparing'] ?? 0}'),
                _StatCard(label: 'Out for Delivery', value: '${_counts?['out_for_delivery'] ?? 0}'),
                _StatCard(label: 'Pending QR Payments', value: '${_counts?['pending_qr'] ?? 0}', color: MegaTheme.gold),
                const SizedBox(height: 24),
                Text('Delivery Staff Identities (exactly 2)', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                ..._slots.map((s) => Card(
                      child: ListTile(
                        title: Text(s['display_name'] ?? 'Unconfigured'),
                        subtitle: Text('Slot ${s['id']} • ${s['configured'] == true ? 'Configured' : 'Pending name'}'),
                        trailing: IconButton(
                          icon: const Icon(Icons.edit),
                          onPressed: () => _editSlotName(s),
                        ),
                      ),
                    )),
                const SizedBox(height: 16),
                const Text(
                  'Admin can only edit the two existing identity names. A third identity cannot be created.',
                  style: TextStyle(fontSize: 12, color: MegaTheme.textSecondary),
                ),
              ],
            ),
    );
  }

  Future<void> _editSlotName(Map<String, dynamic> slot) async {
    final ctrl = TextEditingController(text: slot['display_name'] ?? '');
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Edit Slot ${slot['id']} Name'),
        content: TextField(controller: ctrl, decoration: const InputDecoration(labelText: 'Display name')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, ctrl.text.trim()),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (result == null) return;
    try {
      final api = context.read<ApiClient>();
      await api.patch('/api/v1/admin/delivery-slots/${slot['id']}', body: {'display_name': result});
      _load();
    } catch (_) {}
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;
  const _StatCard({required this.label, required this.value, this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: Theme.of(context).textTheme.titleLarge),
            Text(
              value,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: color ?? MegaTheme.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
