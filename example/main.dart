import 'package:flutter/material.dart';
import 'package:fluent_icons_kit/fluent_icons_kit.dart';

void main() => runApp(const FluentIconsExample());

class FluentIconsExample extends StatelessWidget {
  const FluentIconsExample({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fluent Icons Kit Example',
      home: Scaffold(
        appBar: AppBar(title: const Text('Fluent Icons Kit')),
        body: Center(
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(FluentIcons.line.search, size: 36),
              const SizedBox(width: 16),
              Icon(FluentIcons.filled.home, size: 36),
              const SizedBox(width: 16),
              Icon(FluentIcons.line.heart, size: 36),
            ],
          ),
        ),
      ),
    );
  }
}
