import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';

class AdminOrdersScreen extends StatefulWidget {
  const AdminOrdersScreen({super.key});

  @override
  State<AdminOrdersScreen> createState() => _AdminOrdersScreenState();
}

class _AdminOrdersScreenState extends State<AdminOrdersScreen> {
  List<dynamic> _orders = [];
  bool _loading = true;
  String? _error;
  String _status = 'all';

  static const _statuses = <String>[
    'all',
    'new',
    'preparing',
    'out_for_delivery',
    'delivered',
    'cancelled',
  ];

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final api = context.read<ApiClient>();
      final query = _status == 'all' ? '' : '?status=$_status';
      final response = await api.get('/api/v1/admin/orders$query');
      final data = response['orders'];

      if (!mounted) return;
      setState(() {
        _orders = data is List ? data : <dynamic>[];
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _text(dynamic value, [String fallback = 'Not provided']) {
    if (value == null || value.toString().trim().isEmpty) return fallback;
    return value.toString();
  }

  String _money(dynamic value) => 'Rs. ${_text(value, '0.00')}';


  Future<void> _updateOrderStatus(Map<String, dynamic> order) async {
    final orderId = order['id']?.toString();
    if (orderId == null || orderId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Order ID is missing.')),
      );
      return;
    }

    const transitions = <String, List<String>>{
      'new': ['accepted', 'rejected', 'cancelled'],
      'accepted': ['preparing', 'cancelled'],
      'preparing': ['ready_for_delivery', 'cancelled'],
      'ready_for_delivery': ['assigned', 'cancelled'],
      'assigned': ['out_for_delivery', 'cancelled'],
      'out_for_delivery': ['delivered', 'cancelled'],
    };

    final current = '${order['status'] ?? 'new'}';
    final choices = transitions[current] ?? <String>[];
    if (choices.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No further status changes allowed from $current.')),
      );
      return;
    }

    String selected = choices.first;
    final nextStatus = await showDialog<String>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Update order status'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Current status: ${current.replaceAll('_', ' ')}'),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: selected,
                decoration: const InputDecoration(
                  labelText: 'New status',
                  border: OutlineInputBorder(),
                ),
                items: choices.map((status) {
                  return DropdownMenuItem(
                    value: status,
                    child: Text(status.replaceAll('_', ' ')),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setDialogState(() => selected = value);
                  }
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(dialogContext).pop(selected),
              child: const Text('Update'),
            ),
          ],
        ),
      ),
    );

    if (nextStatus == null || !mounted) return;

    try {
      final api = context.read<ApiClient>();
      await api.patch(
        '/api/v1/orders/$orderId/status',
        body: {'status': nextStatus},
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Order status updated to ${nextStatus.replaceAll('_', ' ')}.'),
        ),
      );
      await _loadOrders();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Status update failed: $e')),
      );
    }
  }

  void _showOrderDetails(Map<String, dynamic> order) {
    final customerValue = order['customer'];
    final customer = customerValue is Map
        ? Map<String, dynamic>.from(customerValue)
        : <String, dynamic>{};

    final addressValue = order['address'];
    final address = addressValue is Map
        ? Map<String, dynamic>.from(addressValue)
        : <String, dynamic>{};

    final assignmentValue = order['assignment'];
    final assignment = assignmentValue is Map
        ? Map<String, dynamic>.from(assignmentValue)
        : <String, dynamic>{};

    final itemsValue = order['items'];
    final items = itemsValue is List ? itemsValue : <dynamic>[];

    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text('Order ${_text(order['order_number'], order['id']?.toString() ?? '')}'),
        content: SizedBox(
          width: 520,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                _section('Order & Payment'),
                _line('Status', order['status']),
                _line('Payment method', order['payment_method']),
                _line('Payment status', order['payment_status']),
                _line('Subtotal', _money(order['subtotal'])),
                _line('Delivery fee', _money(order['delivery_fee'])),
                _line('Discount', _money(order['discount_amount'])),
                _line('Total', _money(order['total'])),
                _line('Created', order['created_at']),
                const Divider(),
                _section('Customer'),
                _line('Type', order['is_guest'] == true ? 'Guest order' : 'Registered customer'),
                _line('Name', customer['full_name'] ?? order['guest_name']),
                _line('Phone', customer['phone'] ?? order['guest_phone']),
                _line('Email', customer['email']),
                _line('Customer ID', customer['id'] ?? order['user_id']),
                const Divider(),
                _section('Delivery Address'),
                _line('Address', address['full_address']),
                _line('Landmark', address['landmark']),
                _line('Latitude', address['latitude']),
                _line('Longitude', address['longitude']),
                const Divider(),
                _section('Items (${items.length})'),
                if (items.isEmpty)
                  const Text('No item details returned.')
                else
                  ...items.map((rawItem) {
                    final item = rawItem is Map
                        ? Map<String, dynamic>.from(rawItem)
                        : <String, dynamic>{};
                    final name = item['food_name_en'] ??
                        item['food_name_ne'] ??
                        item['name'] ??
                        'Food item';
                    final customValue = item['customizations'];
                    final customizations =
                        customValue is List ? customValue : <dynamic>[];

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '$name  × ${_text(item['quantity'], '1')}',
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                          Text('Unit price: ${_money(item['unit_price'])}'),
                          Text('Line total: ${_money(item['line_total'])}'),
                          ...customizations.map((rawCustomization) {
                            final c = rawCustomization is Map
                                ? Map<String, dynamic>.from(rawCustomization)
                                : <String, dynamic>{};
                            return Text(
                              '  • ${_text(c['group_name'], '')}: ${_text(c['option_name'], '')}'
                              ' (${_money(c['price_delta'])})',
                            );
                          }),
                        ],
                      ),
                    );
                  }),
                const Divider(),
                _section('Delivery Assignment'),
                _line('Delivery slot ID', assignment['delivery_slot_id']),
                _line('Staff user ID', assignment['staff_user_id']),
                _line('Assigned at', assignment['assigned_at']),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Close'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(dialogContext).pop();
              _updateOrderStatus(order);
            },
            icon: const Icon(Icons.edit_outlined),
            label: const Text('Update status'),
          ),
        ],
      ),
    );
  }

  Widget _section(String title) => Padding(
        padding: const EdgeInsets.only(top: 8, bottom: 6),
        child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      );

  Widget _line(String label, dynamic value) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Text('$label: ${_text(value)}'),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('All Orders'),
        actions: [
          IconButton(
            tooltip: 'Refresh orders',
            onPressed: _loading ? null : _loadOrders,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              children: _statuses.map((status) {
                final selected = _status == status;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(status == 'all' ? 'All orders' : status.replaceAll('_', ' ')),
                    selected: selected,
                    onSelected: (value) {
                      if (!value || _status == status) return;
                      setState(() => _status = status);
                      _loadOrders();
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.error_outline, size: 42),
                              const SizedBox(height: 12),
                              Text(_error!, textAlign: TextAlign.center),
                              const SizedBox(height: 12),
                              ElevatedButton(
                                onPressed: _loadOrders,
                                child: const Text('Try again'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : _orders.isEmpty
                        ? RefreshIndicator(
                            onRefresh: _loadOrders,
                            child: ListView(
                              children: const [
                                SizedBox(height: 150),
                                Center(child: Text('No orders found.')),
                              ],
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: _loadOrders,
                            child: ListView.separated(
                              padding: const EdgeInsets.all(12),
                              itemCount: _orders.length,
                              separatorBuilder: (_, __) => const SizedBox(height: 8),
                              itemBuilder: (context, index) {
                                final raw = _orders[index];
                                final order = raw is Map
                                    ? Map<String, dynamic>.from(raw)
                                    : <String, dynamic>{};
                                final customerValue = order['customer'];
                                final customer = customerValue is Map
                                    ? Map<String, dynamic>.from(customerValue)
                                    : <String, dynamic>{};
                                final addressValue = order['address'];
                                final address = addressValue is Map
                                    ? Map<String, dynamic>.from(addressValue)
                                    : <String, dynamic>{};

                                final name = customer['full_name'] ??
                                    order['guest_name'] ??
                                    (order['is_guest'] == true ? 'Guest customer' : 'Customer details unavailable');

                                return Card(
                                  child: ListTile(
                                    contentPadding: const EdgeInsets.all(14),
                                    title: Text(
                                      'Order ${_text(order['order_number'], order['id']?.toString() ?? '')}',
                                      style: const TextStyle(fontWeight: FontWeight.bold),
                                    ),
                                    subtitle: Padding(
                                      padding: const EdgeInsets.only(top: 6),
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text('Customer: $name'),
                                          Text('Phone: ${_text(customer['phone'] ?? order['guest_phone'])}'),
                                          Text('Status: ${_text(order['status'])} · Payment: ${_text(order['payment_status'])}'),
                                          Text('Address: ${_text(address['full_address'])}'),
                                          const SizedBox(height: 4),
                                          Text(
                                            _money(order['total']),
                                            style: const TextStyle(fontWeight: FontWeight.bold),
                                          ),
                                        ],
                                      ),
                                    ),
                                    trailing: const Icon(Icons.chevron_right),
                                    onTap: () => _showOrderDetails(order),
                                  ),
                                );
                              },
                            ),
                          ),
          ),
        ],
      ),
    );
  }
}