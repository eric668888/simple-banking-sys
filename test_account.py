import unittest
import decimal
from account import Account, TWO_PLACES

# Set precision for decimal calculations
decimal.getcontext().prec = 28

class TestAccount(unittest.TestCase):
    # Unit tests for the Account class.

    def test_account_creation_valid(self):
        # Test successful creation of an account with valid parameters
        acc = Account("ACC001", "Test User", decimal.Decimal('100.00'))
        self.assertEqual(acc.get_account_number(), "ACC001")
        self.assertEqual(acc.get_account_holder_name(), "Test User")
        self.assertEqual(acc.get_balance(), decimal.Decimal('100.00').quantize(TWO_PLACES))

    def test_account_creation_default_balance(self):
        # Test account creation with default initial balance (0.00)
        acc = Account("ACC002", "Another User")
        self.assertEqual(acc.get_balance(), decimal.Decimal('0.00').quantize(TWO_PLACES))

    def test_account_creation_zero_balance(self):
        # Test account creation with explicit zero initial balance
        acc = Account("ACC003", "Zero Balance User", decimal.Decimal('0.00'))
        self.assertEqual(acc.get_balance(), decimal.Decimal('0.00').quantize(TWO_PLACES))

    def test_account_creation_invalid_initial_balance_negative(self):
        # Test account creation with a negative initial balance
        with self.assertRaisesRegex(ValueError, "Initial balance cannot be negative."):
            Account("ACC004", "Negative User", decimal.Decimal('-50.00'))

    def test_account_creation_invalid_initial_balance_type(self):
        # Test account creation with a non-Decimal initial balance
        with self.assertRaisesRegex(TypeError, "Initial balance must be a Decimal value."):
            Account("ACC005", "Type Error User", 100) # type: ignore

    def test_account_creation_invalid_name_empty(self):
        # Test account creation with an empty name
        with self.assertRaisesRegex(ValueError, "Account holder name must be a non-empty string."):
            Account("ACC006", "", decimal.Decimal('10.00'))

    def test_account_creation_invalid_name_none(self):
        # Test account creation with name as None
        with self.assertRaisesRegex(ValueError, "Account holder name must be a non-empty string."):
            Account("ACC007", None, decimal.Decimal('10.00')) # type: ignore

    def test_account_creation_invalid_account_number_empty(self):
        # Test account creation with an empty account number
        with self.assertRaisesRegex(ValueError, "Account number must be a non-empty string."):
            Account("", "Valid Name", decimal.Decimal('10.00'))

    def test_account_creation_invalid_account_number_none(self):
        # Test account creation with account number as None
        with self.assertRaisesRegex(ValueError, "Account number must be a non-empty string."):
            Account(None, "Valid Name", decimal.Decimal('10.00')) # type: ignore

    def test_deposit_valid(self):
        # Test a valid deposit operation
        acc = Account("ACC100", "Depositor", decimal.Decimal('100.00'))
        acc.deposit(decimal.Decimal('50.50'))
        self.assertEqual(acc.get_balance(), decimal.Decimal('150.50').quantize(TWO_PLACES))

    def test_deposit_multiple(self):
        # Test multiple deposit operations
        acc = Account("ACC101", "Multi Depositor", decimal.Decimal('10.25'))
        acc.deposit(decimal.Decimal('10.25'))
        acc.deposit(decimal.Decimal('5.50'))
        self.assertEqual(acc.get_balance(), decimal.Decimal('26.00').quantize(TWO_PLACES))

    def test_deposit_invalid_amount_zero(self):
        # Test depositing zero amount
        acc = Account("ACC102", "Zero Depositor", decimal.Decimal('100.00'))
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive."):
            acc.deposit(decimal.Decimal('0.00'))

    def test_deposit_invalid_amount_negative(self):
        # Test depositing a negative amount
        acc = Account("ACC103", "Negative Depositor", decimal.Decimal('100.00'))
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive."):
            acc.deposit(decimal.Decimal('-50.00'))

    def test_deposit_invalid_amount_type(self):
        # Test depositing a non-Decimal amount
        acc = Account("ACC104", "Type Error Depositor", decimal.Decimal('100.00'))
        with self.assertRaisesRegex(TypeError, "Deposit amount must be a Decimal value."):
            acc.deposit(50) # type: ignore

    def test_withdraw_valid(self):
        # Test a valid withdrawal operation
        acc = Account("ACC200", "Withdrawer", decimal.Decimal('100.00'))
        acc.withdraw(decimal.Decimal('30.75'))
        self.assertEqual(acc.get_balance(), decimal.Decimal('69.25').quantize(TWO_PLACES))

    def test_withdraw_all_funds(self):
        # Test withdrawing the entire balance
        acc = Account("ACC201", "Empty Account User", decimal.Decimal('50.00'))
        acc.withdraw(decimal.Decimal('50.00'))
        self.assertEqual(acc.get_balance(), decimal.Decimal('0.00').quantize(TWO_PLACES))

    def test_withdraw_insufficient_funds(self):
        # Test withdrawal attempt with insufficient funds
        acc = Account("ACC202", "Overdraft User", decimal.Decimal('50.00'))
        with self.assertRaisesRegex(ValueError, "Insufficient funds for this withdrawal."):
            acc.withdraw(decimal.Decimal('50.01'))
        self.assertEqual(acc.get_balance(), decimal.Decimal('50.00')) # Balance should remain unchanged

    def test_withdraw_invalid_amount_zero(self):
        # Test withdrawing zero amount
        acc = Account("ACC203", "Zero Withdrawer", decimal.Decimal('100.00'))
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive."):
            acc.withdraw(decimal.Decimal('0.00'))

    def test_withdraw_invalid_amount_negative(self):
        # Test withdrawing a negative amount
        acc = Account("ACC204", "Negative Withdrawer", decimal.Decimal('100.00'))
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive."):
            acc.withdraw(decimal.Decimal('-50.00'))

    def test_withdraw_invalid_amount_type(self):
        # Test withdrawing a non-Decimal amount
        acc = Account("ACC205", "Type Error Withdrawer", decimal.Decimal('100.00'))
        with self.assertRaisesRegex(TypeError, "Withdrawal amount must be a Decimal value."):
            acc.withdraw(50) # type: ignore

    def test_get_balance(self):
        # Test the get_balance method for correct formatting
        balance_val = decimal.Decimal('123.456')
        acc = Account("ACC300", "Balance Checker", balance_val)
        # Account __init__ should quantize. get_balance should also ensure it.
        self.assertEqual(acc.get_balance(), decimal.Decimal('123.46').quantize(TWO_PLACES))
        acc.deposit(decimal.Decimal('0.001')) # This will be added, then quantized
        # 123.456 + 0.001 = 123.457. Quantized to 123.46
        self.assertEqual(acc.get_balance(), decimal.Decimal('123.46').quantize(TWO_PLACES))


    def test_string_representation(self):
        # Test the __str__ method for correct output format
        acc = Account("ACC999", "String Test User", decimal.Decimal('99.99'))
        expected_str = "Account Number: ACC999, Holder: String Test User, Balance: 99.99"
        self.assertEqual(str(acc), expected_str)

    def test_precision_after_operations(self):
        # Test that balance precision is maintained after several operations
        acc = Account("ACC400", "Precision Test", decimal.Decimal('10.003')) # Initial should be 10.00
        self.assertEqual(acc.get_balance(), decimal.Decimal('10.00'))

        acc.deposit(decimal.Decimal('0.007')) # 10.00 + 0.007 = 10.007 -> 10.01
        self.assertEqual(acc.get_balance(), decimal.Decimal('10.01'))

        acc.deposit(decimal.Decimal('1.111')) # 10.01 + 1.111 = 11.121 -> 11.12
        self.assertEqual(acc.get_balance(), decimal.Decimal('11.12'))

        acc.withdraw(decimal.Decimal('0.005')) # 11.12 - 0.005 = 11.115 -> 11.12 ( Banker's rounding or specific quantize mode)
                                        
        self.assertEqual(acc.get_balance(), decimal.Decimal('11.12').quantize(TWO_PLACES))

        acc2 = Account("ACC401", "Precision Test 2", decimal.Decimal('11.115')) # Initial will be 11.12
        self.assertEqual(acc2.get_balance(), decimal.Decimal('11.12'))
        acc2.withdraw(decimal.Decimal('0.001')) # 11.12 - 0.001 = 11.119 -> 11.12
        self.assertEqual(acc2.get_balance(), decimal.Decimal('11.12').quantize(TWO_PLACES))
        acc2.withdraw(decimal.Decimal('0.008')) # 11.12 - 0.008 = 11.112 -> 11.11
        self.assertEqual(acc2.get_balance(), decimal.Decimal('11.11').quantize(TWO_PLACES))


if __name__ == '__main__':
    unittest.main()