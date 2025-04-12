import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/group_expense.dart';
import '../models/group_member.dart';
import '../services/api_service.dart';
import '../widgets/custom_split_form.dart';

extension StringExtension on String {
  String capitalize() {
    return "${this[0].toUpperCase()}${substring(1)}";
  }
}

class AddGroupExpenseScreen extends StatefulWidget {
  final int groupId;
  final VoidCallback onExpenseAdded;

  const AddGroupExpenseScreen({
    Key? key,
    required this.groupId,
    required this.onExpenseAdded,
  }) : super(key: key);

  @override
  _AddGroupExpenseScreenState createState() => _AddGroupExpenseScreenState();
}

class _AddGroupExpenseScreenState extends State<AddGroupExpenseScreen> {
  final _formKey = GlobalKey<FormState>();
  final _apiService = ApiService();

  DateTime _selectedDate = DateTime.now();
  String? _selectedCategory;
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  String _splitType = 'equal';
  bool _isLoading = false;
  bool _isLoadingMembers = false;
  Map<int, double>? _customSplits;
  List<GroupMember> _groupMembers = [];

  final _categories = [
    'Food',
    'Transportation',
    'Shopping',
    'Bills',
    'Entertainment',
    'Health',
    'Education',
    'Other'
  ];

  @override
  void initState() {
    super.initState();
    _loadGroupMembers();
  }

  Future<void> _loadGroupMembers() async {
    setState(() => _isLoadingMembers = true);
    try {
      final members = await _apiService.getGroupMembers(widget.groupId);
      setState(() {
        _groupMembers = members;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading group members: $e')),
      );
    } finally {
      setState(() => _isLoadingMembers = false);
    }
  }

  Future<void> _selectDate(BuildContext context) async {
    final ThemeData theme = Theme.of(context);
    final bool isDarkMode = theme.brightness == Brightness.dark;

    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: theme.copyWith(
            colorScheme: isDarkMode
                ? const ColorScheme.dark(
                    primary: Colors.blue,
                    onPrimary: Colors.white,
                    surface: Color(0xFF303030),
                    onSurface: Colors.white,
                  )
                : const ColorScheme.light(
                    primary: Colors.blue,
                    onPrimary: Colors.white,
                    surface: Colors.white,
                    onSurface: Colors.black,
                  ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
    }
  }

  Future<void> _submitExpense() async {
    if (_formKey.currentState!.validate()) {
      if (_splitType == 'custom') {
        if (_groupMembers.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Cannot create custom split with no group members'),
            ),
          );
          return;
        }
        
        if (_customSplits == null ||
            (_customSplits!.values.fold<double>(0.0, (sum, value) => sum + value) - 100.0).abs() >
                0.01) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Custom split percentages must sum to 100%'),
            ),
          );
          return;
        }
      }

      setState(() => _isLoading = true);

      try {
        final expense = GroupExpense(
          id: 0,
          groupId: widget.groupId,
          paidBy: 0,
          date: _selectedDate,
          category: _selectedCategory!,
          amount: double.parse(_amountController.text),
          description: _descriptionController.text,
          splitType: _splitType,
          customSplits: _splitType == 'custom' ? _customSplits : null,
          splits: [],
        );

        await _apiService.createGroupExpense(widget.groupId, expense);
        if (mounted) {
          widget.onExpenseAdded();
          Navigator.pop(context);
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error adding expense: $e')),
          );
        }
      } finally {
        if (mounted) {
          setState(() => _isLoading = false);
        }
      }
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Widget _buildSplitTypeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DropdownButtonFormField<String>(
          value: _splitType,
          decoration: const InputDecoration(
            labelText: 'Split Type',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.group),
          ),
          items: ['equal', 'custom']
              .map((type) => DropdownMenuItem(
                    value: type,
                    child: Text(type.capitalize()),
                  ))
              .toList(),
          onChanged: (value) => setState(() => _splitType = value!),
          validator: (value) => value == null ? 'Please select a split type' : null,
        ),
        if (_splitType == 'custom') ...[
          const SizedBox(height: 16),
          const Text(
            'Custom Split Percentages',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          if (_isLoadingMembers)
            const Center(child: CircularProgressIndicator())
          else
            CustomSplitForm(
              members: _groupMembers,
              onSplitsChanged: (splits) => _customSplits = splits,
            ),
        ],
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Group Expense'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              InkWell(
                onTap: () => _selectDate(context),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Date',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Text(
                    DateFormat('MMMM dd, yyyy').format(_selectedDate),
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedCategory,
                decoration: const InputDecoration(
                  labelText: 'Category',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.category),
                ),
                items: _categories
                    .map((category) => DropdownMenuItem(
                          value: category,
                          child: Text(category),
                        ))
                    .toList(),
                onChanged: (value) => setState(() => _selectedCategory = value),
                validator: (value) =>
                    value == null ? 'Please select a category' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _amountController,
                decoration: const InputDecoration(
                  labelText: 'Amount',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.attach_money),
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an amount';
                  }
                  if (double.tryParse(value) == null) {
                    return 'Please enter a valid number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.description),
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 16),
              _buildSplitTypeSelector(),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _submitExpense,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator()
                    : const Text('Save Expense', style: TextStyle(fontSize: 16)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
