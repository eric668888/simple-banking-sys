import unittest
import decimal
import os
import csv
from account import Account, TWO_PLACES
from banking_system import BankingSystem

# Set precision for decimal calculations
decimal.getcontext().prec = 28
TEST_CSV_FILE = "test_bank_data.csv"
TEST_CSV_BACKUP_FILE = "test_bank_data_backup.csv" # For specific tests

class TestBankingSystem(unittest.TestCase):
    # Unit tests for the BankingSystem class.

    def setUp(self):
        # Initializes a BankingSystem instance with the test CSV file.
        self.delete_test_csv_files() # Clean up before each test
        self.system = BankingSystem(csv_file_path=TEST_CSV_FILE)

    def tearDown(self):
        self.delete_test_csv_files()

    def delete_test_csv_files(self):
        # Helper to delete test CSV files.
        if os.path.exists(TEST_CSV_FILE):
            os.remove(TEST_CSV_FILE)
        if os.path.exists(TEST_CSV_BACKUP_FILE):
            os.remove(TEST_CSV_BACKUP_FILE)

    def test_initialization_no_file(self):
        # Test system initialization when no CSV file exists.
        self.assertEqual(len(self.system._accounts), 0)
        self.assertEqual(self.system._next_account_number, 1) # Default starting number

    def test_create_account(self):
        # Test creating a new account.
        acc1 = self.system.create_account("Alice", decimal.Decimal('100.00'))
        self.assertIsNotNone(acc1)
        self.assertEqual(acc1.get_account_holder_name(), "Alice")
        self.assertEqual(acc1.get_balance(), decimal.Decimal('100.00').quantize(TWO_PLACES))
        self.assertIn(acc1.get_account_number(), self.system._accounts)
        self.assertEqual(self.system._next_account_number, 2) # ACC001 created, next should be 2

        acc2 = self.system.create_account("Bob") # Default balance
        self.assertEqual(acc2.get_balance(), decimal.Decimal('0.00').quantize(TWO_PLACES))
        self.assertEqual(self.system._next_account_number, 3) # ACC002 created, next should be 3
        
        # Test account number generation (simple check for format)
        self.assertTrue(acc1.get_account_number().startswith("ACC"))
        self.assertTrue(acc2.get_account_number().startswith("ACC"))
        self.assertNotEqual(acc1.get_account_number(), acc2.get_account_number())

    def test_create_account_invalid_name(self):
        # Test creating account with invalid name.
        with self.assertRaisesRegex(ValueError, "Account holder name must be a non-empty string."):
            self.system.create_account("", decimal.Decimal('50.00'))

    def test_create_account_invalid_balance(self):
        # Test creating account with invalid initial balance.
        with self.assertRaisesRegex(ValueError, "Initial balance cannot be negative."):
            self.system.create_account("Bad Balance User", decimal.Decimal('-10.00'))
        with self.assertRaisesRegex(TypeError, "Initial balance must be a Decimal value."):
            self.system.create_account("Type Error User", 100) # type: ignore


    def test_find_account(self):
        # Test finding an existing and non-existing account.
        acc = self.system.create_account("Carol", decimal.Decimal('200.00'))
        found_acc = self.system.find_account(acc.get_account_number())
        self.assertEqual(found_acc, acc)
        
        non_existent_acc = self.system.find_account("ACC999")
        self.assertIsNone(non_existent_acc)

    def test_deposit_to_account(self):
        # Test depositing funds into an account.
        acc = self.system.create_account("Dave", decimal.Decimal('50.00'))
        acc_num = acc.get_account_number()

        self.assertTrue(self.system.deposit_to_account(acc_num, decimal.Decimal('25.50')))
        self.assertEqual(acc.get_balance(), decimal.Decimal('75.50').quantize(TWO_PLACES))

        # Test deposit to non-existent account
        self.assertFalse(self.system.deposit_to_account("ACC999", decimal.Decimal('10.00')))

        # Test invalid deposit amount (negative)
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive."):
            self.system.deposit_to_account(acc_num, decimal.Decimal('-5.00'))

    def test_withdraw_from_account(self):
        # Test withdrawing funds from an account.
        acc = self.system.create_account("Eve", decimal.Decimal('100.00'))
        acc_num = acc.get_account_number()

        self.assertTrue(self.system.withdraw_from_account(acc_num, decimal.Decimal('30.25')))
        self.assertEqual(acc.get_balance(), decimal.Decimal('69.75').quantize(TWO_PLACES))

        # Test withdraw from non-existent account
        self.assertFalse(self.system.withdraw_from_account("ACC999", decimal.Decimal('10.00')))

        # Test insufficient funds
        with self.assertRaisesRegex(ValueError, "Insufficient funds for this withdrawal."):
            self.system.withdraw_from_account(acc_num, decimal.Decimal('1000.00'))
        self.assertEqual(acc.get_balance(), decimal.Decimal('69.75')) # Balance unchanged

        # Test invalid withdrawal amount (zero)
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive."):
            self.system.withdraw_from_account(acc_num, decimal.Decimal('0.00'))

    def test_transfer_money(self):
        # Test transferring money between accounts.
        acc_f = self.system.create_account("Frank", decimal.Decimal('200.00'))
        acc_g = self.system.create_account("Grace", decimal.Decimal('50.00'))
        from_acc_num = acc_f.get_account_number()
        to_acc_num = acc_g.get_account_number()

        self.assertTrue(self.system.transfer_money(from_acc_num, to_acc_num, decimal.Decimal('75.00')))
        self.assertEqual(acc_f.get_balance(), decimal.Decimal('125.00').quantize(TWO_PLACES))
        self.assertEqual(acc_g.get_balance(), decimal.Decimal('125.00').quantize(TWO_PLACES))

        # Test transfer with insufficient funds
        with self.assertRaisesRegex(ValueError, "Insufficient funds in account .* for transfer."):
            self.system.transfer_money(from_acc_num, to_acc_num, decimal.Decimal('200.00')) # Frank only has 125
        self.assertEqual(acc_f.get_balance(), decimal.Decimal('125.00')) # Unchanged
        self.assertEqual(acc_g.get_balance(), decimal.Decimal('125.00')) # Unchanged

        # Test transfer to non-existent account
        with self.assertRaisesRegex(ValueError, "Recipient account ACC999 not found."):
            self.system.transfer_money(from_acc_num, "ACC999", decimal.Decimal('10.00'))

        # Test transfer from non-existent account
        with self.assertRaisesRegex(ValueError, "Sender account ACC888 not found."):
            self.system.transfer_money("ACC888", to_acc_num, decimal.Decimal('10.00'))
        
        # Test transfer to self
        with self.assertRaisesRegex(ValueError, "Cannot transfer money to the same account."):
            self.system.transfer_money(from_acc_num, from_acc_num, decimal.Decimal('10.00'))

        # Test transfer negative amount
        with self.assertRaisesRegex(ValueError, "Transfer amount must be positive."):
            self.system.transfer_money(from_acc_num, to_acc_num, decimal.Decimal('-10.00'))


    def test_save_and_load_csv(self):
        # Test saving account data to CSV and loading it back.
        acc1 = self.system.create_account("Heidi", decimal.Decimal('1000.50'))
        acc2 = self.system.create_account("Ivan", decimal.Decimal('250.75'))
        initial_next_acc_num = self.system._next_account_number # Should be 3 after creating Heidi and Ivan

        self.system.save_to_csv()
        self.assertTrue(os.path.exists(TEST_CSV_FILE))

        # Create a new system instance to load the data
        loaded_system = BankingSystem(csv_file_path=TEST_CSV_FILE)
        self.assertEqual(len(loaded_system._accounts), 2)
        self.assertEqual(loaded_system._next_account_number, initial_next_acc_num)

        loaded_acc1 = loaded_system.find_account(acc1.get_account_number())
        loaded_acc2 = loaded_system.find_account(acc2.get_account_number())

        self.assertIsNotNone(loaded_acc1)
        self.assertIsNotNone(loaded_acc2)
        self.assertEqual(loaded_acc1.get_account_holder_name(), "Heidi")
        self.assertEqual(loaded_acc1.get_balance(), decimal.Decimal('1000.50').quantize(TWO_PLACES))
        self.assertEqual(loaded_acc2.get_account_holder_name(), "Ivan")
        self.assertEqual(loaded_acc2.get_balance(), decimal.Decimal('250.75').quantize(TWO_PLACES))

        # Create another account to check if next_account_number was loaded correctly
        acc3_loaded = loaded_system.create_account("Judy", decimal.Decimal('50.00'))
        self.assertEqual(acc3_loaded.get_account_number(), f"ACC{initial_next_acc_num:03d}") # e.g. ACC003
        self.assertEqual(loaded_system._next_account_number, initial_next_acc_num + 1)


    def test_load_from_empty_csv(self):
        # Test loading from an empty CSV file.
        with open(TEST_CSV_FILE, 'w', newline='') as f:
            pass # Just create it
        
        empty_load_system = BankingSystem(csv_file_path=TEST_CSV_FILE)
        self.assertEqual(len(empty_load_system._accounts), 0)
        self.assertEqual(empty_load_system._next_account_number, 1) # Default if file is empty or unparsable

    def test_load_from_csv_with_only_metadata(self):
        # Test loading from a CSV file that only contains the metadata line.
        with open(TEST_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["METADATA", "15"]) # next_account_number is 15

        meta_system = BankingSystem(csv_file_path=TEST_CSV_FILE)
        self.assertEqual(len(meta_system._accounts), 0)
        self.assertEqual(meta_system._next_account_number, 15)

    def test_load_from_csv_with_malformed_data_row(self):
        # Test loading from CSV with a row that has incorrect number of columns or bad balance.
        with open(TEST_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["METADATA", "3"])
            writer.writerow(["account_number", "name", "balance"])
            writer.writerow(["ACC001", "Good User", "100.00"])
            writer.writerow(["ACC002", "Bad Row User"]) # Missing balance
            writer.writerow(["ACC003", "Another Good User", "50.00", "ExtraColumn"]) # Extra column
            writer.writerow(["ACC004", "Bad Balance User", "NOT_A_DECIMAL"])

        # Suppress print warnings during this test for cleaner output
        import builtins
        original_print = builtins.print
        builtins.print = lambda *args, **kwargs: None

        try:
            load_system = BankingSystem(csv_file_path=TEST_CSV_FILE)
        finally:
            builtins.print = original_print # Restore print

        self.assertEqual(len(load_system._accounts), 1) # Only ACC001 should load
        loaded_acc = load_system.find_account("ACC001")
        self.assertIsNotNone(loaded_acc)
        self.assertEqual(loaded_acc.get_balance(), decimal.Decimal('100.00'))
        # _next_account_number should be updated based on successfully loaded accounts
        # and metadata. If ACC001 (numeric 1) loaded, and metadata was 3, it should be 3.
        # If metadata was 1, and ACC001 loaded, it should be 2.
        # The logic in BankingSystem._load_from_csv is:
        # self._next_account_number = int(metadata_row[1])
        # ... then later, if max_loaded_acc_num_val >= self._next_account_number: self._next_account_number = max_loaded_acc_num_val + 1
        # Here, metadata is 3. Max loaded is 1 (from ACC001). So it should remain 3.
        self.assertEqual(load_system._next_account_number, 3)


    def test_load_from_csv_updates_next_account_number_correctly(self):
        """
        Test that _next_account_number is correctly set higher than any loaded account numbers,
        even if metadata was lower.
        """
        with open(TEST_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["METADATA", "1"]) # Metadata says next is 1 (too low)
            writer.writerow(["account_number", "name", "balance"])
            writer.writerow(["ACC005", "User Five", "10.00"]) # Highest account number is 5

        load_system = BankingSystem(csv_file_path=TEST_CSV_FILE)
        self.assertEqual(len(load_system._accounts), 1)
        # _next_account_number should be 6 (max loaded 5 + 1)
        self.assertEqual(load_system._next_account_number, 6)


    def test_list_accounts(self):
        """Test listing accounts."""
        self.assertEqual(self.system.list_accounts(), ["No accounts in the system."])
        
        acc1 = self.system.create_account("User One", decimal.Decimal('10.00'))
        acc2 = self.system.create_account("User Two", decimal.Decimal('20.00'))
        
        listed_accounts = self.system.list_accounts()
        self.assertEqual(len(listed_accounts), 2)
        self.assertIn(str(acc1), listed_accounts)
        self.assertIn(str(acc2), listed_accounts)

    def test_account_number_generation_consistency_after_load(self):
        """Test that account numbers continue correctly after loading data."""
        # Setup initial data and save
        self.system.create_account("Alpha", decimal.Decimal('100')) # ACC001, next=2
        self.system.create_account("Beta", decimal.Decimal('200'))  # ACC002, next=3
        self.system.save_to_csv()

        # Load into a new system
        loaded_system = BankingSystem(csv_file_path=TEST_CSV_FILE)
        self.assertEqual(loaded_system._next_account_number, 3) # Should be 3 from saved metadata

        # Create new account in loaded system
        gamma_acc = loaded_system.create_account("Gamma", decimal.Decimal('300'))
        self.assertEqual(gamma_acc.get_account_number(), "ACC003")
        self.assertEqual(loaded_system._next_account_number, 4)


if __name__ == '__main__':
    unittest.main()

