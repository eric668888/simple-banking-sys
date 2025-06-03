import csv
import decimal
import os
from typing import Dict, Optional, List
from account import Account, TWO_PLACES

class BankingSystem:
    """
    Manages a collection of bank accounts and banking operations.
    Handles account creation, transactions, and data persistence via CSV.
    """

    def __init__(self, csv_file_path: str = "bank_data.csv"):
        """
        Initializes the BankingSystem.

        Args:
            csv_file_path (str): The path to the CSV file used for data storage.
                                 Defaults to "bank_data.csv".
        """
        self._accounts: Dict[str, Account] = {}
        self._next_account_number: int = 1 # Simple counter for generating account numbers
        self._csv_file_path: str = csv_file_path
        self._load_from_csv() # Load existing data on initialization

    def _generate_account_number(self) -> str:
        """Generates a new unique account number."""
        # Basic implementation: ACC followed by a zero-padded number.
        # Ensures uniqueness by checking existing accounts and incrementing _next_account_number.
        while True:
            acc_num_str = f"ACC{self._next_account_number:03d}"
            if acc_num_str not in self._accounts:
                return acc_num_str
            self._next_account_number += 1


    def create_account(self, name: str, initial_balance: decimal.Decimal = decimal.Decimal('0.00')) -> Account:
        """
        Creates a new bank account and adds it to the system.

        Args:
            name (str): The name of the account holder.
            initial_balance (Decimal, optional): The starting balance. Defaults to Decimal('0.00').

        Returns:
            Account: The newly created Account object.

        Raises:
            ValueError: If the initial balance is negative or name is invalid.
            TypeError: If initial_balance is not a Decimal.
        """
        if not isinstance(initial_balance, decimal.Decimal):
            raise TypeError("Initial balance must be a Decimal value.")
        if initial_balance < decimal.Decimal('0.00'):
            raise ValueError("Initial balance cannot be negative.")
        if not name or not isinstance(name, str): # Basic name validation
            raise ValueError("Account holder name must be a non-empty string.")

        account_number = self._generate_account_number()
        new_account = Account(account_number, name, initial_balance)
        self._accounts[account_number] = new_account
        self._next_account_number += 1 
        return new_account

    def find_account(self, account_number: str) -> Optional[Account]:
        # Finds an account by its account number
        return self._accounts.get(account_number)

    def deposit_to_account(self, account_number: str, amount: decimal.Decimal) -> bool:
        # Deposits a specified amount into an account
        account = self.find_account(account_number)
        if not account:
            return False
        try:
            account.deposit(amount)
            return True
        except (ValueError, TypeError) as e:
            raise

    def withdraw_from_account(self, account_number: str, amount: decimal.Decimal) -> bool:
        # Withdraws a specified amount from an account.

        account = self.find_account(account_number)
        if not account:
            # print(f"Error: Account {account_number} not found.") # Optional
            return False
        try:
            account.withdraw(amount)
            return True
        except (ValueError, TypeError) as e:
            raise

    def transfer_money(self, from_account_number: str, to_account_number: str, amount: decimal.Decimal) -> bool:
        """
        Transfers money from one account to another.

        Args:
            from_account_number (str): The account number to transfer from.
            to_account_number (str): The account number to transfer to.
            amount (Decimal): The amount to transfer.

        Returns:
            bool: True if the transfer was successful, False otherwise.

        Raises:
            ValueError: If amount is not positive, or if accounts are invalid/same, or insufficient funds.
            TypeError: If amount is not a Decimal.
        """
        if not isinstance(amount, decimal.Decimal):
            raise TypeError("Transfer amount must be a Decimal value.")
        if amount <= decimal.Decimal('0.00'):
            raise ValueError("Transfer amount must be positive.")
        if from_account_number == to_account_number:
            raise ValueError("Cannot transfer money to the same account.")

        from_account = self.find_account(from_account_number)
        to_account = self.find_account(to_account_number)

        if not from_account:
            raise ValueError(f"Sender account {from_account_number} not found.")
        if not to_account:
            raise ValueError(f"Recipient account {to_account_number} not found.")

        if from_account.get_balance() < amount:
            raise ValueError(f"Insufficient funds in account {from_account_number} for transfer.")

        try:
            from_account.withdraw(amount)
            to_account.deposit(amount)
            return True
        except (ValueError, TypeError) as e:
            raise

    def save_to_csv(self) -> None:
        """
        Saves the current state of all accounts and the next account number to a CSV file.
        The CSV file will have a header row for accounts:
        account_number,name,balance
        And a separate mechanism or section for metadata like next_account_number.
        For simplicity, we'll store next_account_number in a separate metadata file or as the first line of the CSV.
        Line 1: METADATA,next_account_number_value
        Line 2: account_number,name,balance (Header for accounts)
        Line 3 onwards: Account data
        """
        try:
            with open(self._csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write metadata (next_account_number)
                writer.writerow(["METADATA", str(self._next_account_number)])
                # Write account data header
                writer.writerow(["account_number", "name", "balance"])
                # Write account data
                for account in self._accounts.values():
                    writer.writerow([
                        account.get_account_number(),
                        account.get_account_holder_name(),
                        str(account.get_balance().quantize(TWO_PLACES)) # Ensure balance is string
                    ])
        except IOError as e:
            print(f"Error saving data to CSV: {e}")

    def _load_from_csv(self) -> None:
        # Loads the system state (accounts and next_account_number) from a CSV file.

        if not os.path.exists(self._csv_file_path):
            print("No data file found. Starting with an empty system.") # Optional
            return

        try:
            with open(self._csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                # Read metadata (next_account_number)
                try:
                    metadata_row = next(reader)
                    if metadata_row and metadata_row[0] == "METADATA":
                        self._next_account_number = int(metadata_row[1])
                    else:
                        self._next_account_number = 1 
                        file.seek(0) # Go back to the start of the file to read headers/data
                except StopIteration:
                    # print("Warning: CSV file is empty or contains no metadata. Using default next_account_number.")
                    self._next_account_number = 1
                    return # Empty file
                except (IndexError, ValueError) as e:
                    # print(f"Warning: Error parsing metadata: {e}. Using default next_account_number.")
                    self._next_account_number = 1
                    file.seek(0) # Reset to try reading as if no metadata line

                # Read account data header
                try:
                    header = next(reader)
                    if header != ["account_number", "name", "balance"]:
                        print(f"Warning: CSV header mismatch. Expected ['account_number', 'name', 'balance'], got {header}.")
                        print("Attempting to load data assuming this is the header anyway or data will be skipped.")
                        pass
                except StopIteration:
                    return # Only metadata, no accounts

                # Read account data
                loaded_accounts_count = 0
                max_loaded_acc_num_val = 0
                for row in reader:
                    if len(row) == 3:
                        try:
                            acc_num, name, balance_str = row
                            balance = decimal.Decimal(balance_str)
                            # Create Account instance (validation happens in Account.__init__)
                            account = Account(acc_num, name, balance)
                            self._accounts[acc_num] = account
                            loaded_accounts_count += 1
                            # If metadata was missing.
                            if acc_num.startswith("ACC"):
                                try:
                                    num_part = int(acc_num[3:])
                                    if num_part >= max_loaded_acc_num_val:
                                        max_loaded_acc_num_val = num_part
                                except ValueError:
                                    pass # Ignore if account number format is unexpected
                        except (ValueError, TypeError, decimal.InvalidOperation) as e:
                            print(f"Warning: Skipping malformed row in CSV: {row} - Error: {e}")
                    else:
                        print(f"Warning: Skipping row with incorrect number of columns: {row}")
                
                # After loading all accounts, ensure _next_account_number is greater than any loaded account number's numeric part.
                if max_loaded_acc_num_val >= self._next_account_number :
                    self._next_account_number = max_loaded_acc_num_val + 1

                if loaded_accounts_count > 0:
                    pass

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Critical error loading data from CSV: {e}. System may be in an inconsistent state.")
            self._accounts.clear()
            self._next_account_number = 1


    def list_accounts(self) -> List[str]:
        # Returns a list of string representations of all accounts
        if not self._accounts:
            return ["No accounts in the system."]
        return [str(account) for account in self._accounts.values()]