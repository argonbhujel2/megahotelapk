import 'package:flutter_test/flutter_test.dart';
import 'package:mega_hotel_delivery/main.dart';

void main() {
  testWidgets('Mega Hotel app starts successfully', (WidgetTester tester) async {
    await tester.pumpWidget(const MegaHotelApp());

    // Allow the splash screen's delayed navigation timer to complete.
    await tester.pump(const Duration(seconds: 6));
    await tester.pumpAndSettle();

    expect(find.byType(MegaHotelApp), findsOneWidget);
  });
}
