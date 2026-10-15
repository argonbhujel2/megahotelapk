import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../theme/mega_theme.dart';
import '../../core/auth_state.dart';
import '../../core/api_client.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> _foods = [];
  List<dynamic> _banners = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final api = context.read<ApiClient>();
      final foodsRes = await api.get('/api/v1/menu/foods');
      final bannersRes = await api.get('/api/v1/banners');
      setState(() {
        _foods = foodsRes['foods'] as List? ?? [];
        _banners = bannersRes['banners'] as List? ?? [];
      });
    } catch (e) {
      setState(() => _error = 'Unable to load menu. Check connection.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mega Hotel'),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart_outlined),
            onPressed: () {
              // Navigate to cart
            },
          ),
          if (auth.isAuthenticated)
            IconButton(
              icon: const Icon(Icons.person_outline),
              onPressed: () {},
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_error!),
                      const SizedBox(height: 12),
                      ElevatedButton(onPressed: _load, child: const Text('Retry')),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
                    padding: const EdgeInsets.only(bottom: 32),
                    children: [
                      if (_banners.isNotEmpty)
                        SizedBox(
                          height: 160,
                          child: PageView.builder(
                            itemCount: _banners.length,
                            itemBuilder: (_, i) {
                              final b = _banners[i];
                              return Container(
                                margin: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: MegaTheme.creamDark,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: Center(
                                  child: Text(
                                    b['title'] ?? 'Promo',
                                    style: Theme.of(context).textTheme.titleLarge,
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        child: Text(
                          'Menu',
                          style: Theme.of(context).textTheme.headlineMedium,
                        ),
                      ),
                      if (_foods.isEmpty)
                        const Padding(
                          padding: EdgeInsets.all(32),
                          child: Center(child: Text('No items available yet.')),
                        )
                      else
                        ..._foods.map((f) => _FoodTile(food: f)),
                      const SizedBox(height: 24),
                      Center(
                        child: TextButton(
                          onPressed: () async {
                            final uri = Uri.parse('https://bamstudio.argan.com.np/');
                            if (await canLaunchUrl(uri)) {
                              await launchUrl(uri, mode: LaunchMode.externalApplication);
                            }
                          },
                          child: const Text(
                            'Technology by BAM Studio',
                            style: TextStyle(fontSize: 12, color: MegaTheme.textSecondary),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }
}

class _FoodTile extends StatelessWidget {
  final Map<String, dynamic> food;
  const _FoodTile({required this.food});

  @override
  Widget build(BuildContext context) {
    final available = food['available'] == true;
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        title: Text(food['name'] ?? food['name_en'] ?? ''),
        subtitle: Text(
          'NPR ${food['base_price'] ?? '0.00'}',
          style: const TextStyle(
            color: MegaTheme.forestGreen,
            fontWeight: FontWeight.w600,
          ),
        ),
        trailing: available
            ? const Icon(Icons.add_circle, color: MegaTheme.forestGreen)
            : const Text('Out of stock', style: TextStyle(color: MegaTheme.error, fontSize: 12)),
        onTap: available
            ? () {
                // Navigate to food detail / customization
              }
            : null,
      ),
    );
  }
}
