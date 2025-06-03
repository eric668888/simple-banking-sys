import decimal
import sys

try:
    from banking_system import BankingSystem
    from account import Account
except ImportError:
    print("Error: Could not import BankingSystem or Account.")
    print("Please ensure banking_system.py and account.py are in the same directory or in PYTHONPATH.")
    sys.exit(1)

# Set precision for decimal context
decimal.getcontext().prec = 28
TWO_PLACES = decimal.Decimal('0.01')

# --- Helper Functions for CLI ---

def get_decimal_input(prompt: str) -> decimal.Decimal | None:
    """
    Prompts the user for a decimal input and handles potential errors.
    Returns a Decimal object or None if input is invalid or user cancels.
    """
    while True:
        try:
            value_str = input(prompt).strip()
            if not value_str: # Allow empty input to cancel/go back
                return None
            value = decimal.Decimal(value_str)
            if value < decimal.Decimal('0.00'): # Often amounts should be non-negative
                print("Amount cannot be negative. Please enter a valid amount or leave blank to cancel.")
                continue
            return value.quantize(TWO_PLACES)
        except decimal.InvalidOperation:
            print("Invalid amount. Please enter a numeric value (e.g., 100.50).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

def get_string_input(prompt: str, allow_empty: bool = False) -> str | None:
    """
    Prompts the user for a string input.
    Returns the string or None if input is empty and not allowed.
    """
    value = input(prompt).strip()
    if not value and not allow_empty:
        print("This field cannot be empty.")
        return None
    return value if value else (None if not allow_empty else "")


# --- CLI Action Functions ---

def handle_create_account(system: BankingSystem):
    """Handles the account creation process."""
    print("\n--- Create New Account ---")
    name = get_string_input("Enter account holder's name: ")
    if name is None:
        print("Account creation cancelled (name not provided).")
        return

    while True:
        balance_str = input("Enter initial balance (e.g., 50.00, press Enter for 0.00): ").strip()
        if not balance_str:
            initial_balance = decimal.Decimal('0.00')
            break
        try:
            initial_balance = decimal.Decimal(balance_str)
            if initial_balance < decimal.Decimal('0.00'):
                print("Initial balance cannot be negative. Please enter a valid amount.")
                continue
            initial_balance = initial_balance.quantize(TWO_PLACES)
            break
        except decimal.InvalidOperation:
            print("Invalid balance format. Please enter a numeric value.")

    try:
        account = system.create_account(name, initial_balance)
        print("\nAccount created successfully!")
        print(f"  Account Number: {account.get_account_number()}")
        print(f"  Holder Name: {account.get_account_holder_name()}")
        print(f"  Balance: ${account.get_balance():.2f}")
    except (ValueError, TypeError) as e:
        print(f"Error creating account: {e}")

def handle_deposit(system: BankingSystem):
    """Handles the deposit process."""
    print("\n--- Deposit Funds ---")
    account_number = get_string_input("Enter account number to deposit into: ")
    if not account_number:
        print("Deposit cancelled (account number not provided).")
        return

    account = system.find_account(account_number)
    if not account:
        print(f"Error: Account {account_number} not found.")
        return

    print(f"Depositing to: {account.get_account_holder_name()} ({account_number})")
    print(f"Current balance: ${account.get_balance():.2f}")
    amount = get_decimal_input("Enter amount to deposit: ")
    if amount is None:
        print("Deposit cancelled.")
        return
    if amount <= decimal.Decimal('0.00'):
        print("Deposit amount must be positive.")
        return

    try:
        if system.deposit_to_account(account_number, amount):
            print("\nDeposit successful!")
            print(f"New balance for {account_number}: ${account.get_balance():.2f}")
        else:
            print("Deposit failed. Please check the details.")
    except (ValueError, TypeError) as e:
        print(f"Error during deposit: {e}")


def handle_withdraw(system: BankingSystem):
    """Handles the withdrawal process."""
    print("\n--- Withdraw Funds ---")
    account_number = get_string_input("Enter account number to withdraw from: ")
    if not account_number:
        print("Withdrawal cancelled (account number not provided).")
        return

    account = system.find_account(account_number)
    if not account:
        print(f"Error: Account {account_number} not found.")
        return

    print(f"Withdrawing from: {account.get_account_holder_name()} ({account_number})")
    print(f"Current balance: ${account.get_balance():.2f}")
    amount = get_decimal_input("Enter amount to withdraw: ")
    if amount is None:
        print("Withdrawal cancelled.")
        return
    if amount <= decimal.Decimal('0.00'):
        print("Withdrawal amount must be positive.")
        return

    try:
        if system.withdraw_from_account(account_number, amount):
            print("\nWithdrawal successful!")
            print(f"New balance for {account_number}: ${account.get_balance():.2f}")
        else:
            print("Withdrawal failed. Please check the details.")
    except (ValueError, TypeError) as e:
        print(f"Error during withdrawal: {e}")


def handle_transfer(system: BankingSystem):
    """Handles the money transfer process."""
    print("\n--- Transfer Funds ---")
    from_account_number = get_string_input("Enter your account number (sender): ")
    if not from_account_number:
        print("Transfer cancelled (sender account not provided).")
        return

    to_account_number = get_string_input("Enter recipient's account number: ")
    if not to_account_number:
        print("Transfer cancelled (recipient account not provided).")
        return

    if from_account_number == to_account_number:
        print("Error: Cannot transfer to the same account.")
        return

    amount = get_decimal_input("Enter amount to transfer: ")
    if amount is None:
        print("Transfer cancelled.")
        return
    if amount <= decimal.Decimal('0.00'):
        print("Transfer amount must be positive.")
        return

    try:
        if system.transfer_money(from_account_number, to_account_number, amount):
            print("\nTransfer successful!")
            sender_acc = system.find_account(from_account_number)
            receiver_acc = system.find_account(to_account_number)
            if sender_acc:
                 print(f"New balance for {from_account_number}: ${sender_acc.get_balance():.2f}")
            if receiver_acc:
                 print(f"New balance for {to_account_number}: ${receiver_acc.get_balance():.2f}")
        else:
            print("Transfer failed. Please check account numbers and funds.")
    except (ValueError, TypeError) as e:
        print(f"Error during transfer: {e}")


def handle_view_account(system: BankingSystem):
    """Handles viewing details of a specific account."""
    print("\n--- View Account Details ---")
    account_number = get_string_input("Enter account number to view: ")
    if not account_number:
        print("View account cancelled (account number not provided).")
        return

    account = system.find_account(account_number)
    if account:
        print("\n--- Account Details ---")
        print(f"  Account Number: {account.get_account_number()}")
        print(f"  Holder Name: {account.get_account_holder_name()}")
        print(f"  Balance: ${account.get_balance():.2f}")
    else:
        print(f"Error: Account {account_number} not found.")


def handle_list_accounts(system: BankingSystem):
    """Handles listing all accounts in the system."""
    print("\n--- All Accounts ---")
    accounts_list = system.list_accounts()
    if not accounts_list or accounts_list == ["No accounts in the system."]:
        print("No accounts found in the system.")
    else:
        for acc_info in accounts_list:
            print(acc_info) # Account.__str__ provides a good format


def display_menu():
    """Displays the main menu options."""
    print("\n===== Simple Banking System =====")
    print("1. Create New Account")
    print("2. Deposit Funds")
    print("3. Withdraw Funds")
    print("4. Transfer Funds")
    print("5. View Account Details")
    print("6. List All Accounts")
    print("7. Exit")
    print("===============================")


def main():
    """Main function to run the banking system CLI."""
    csv_file = "bank_data.csv"
    banking_system = BankingSystem(csv_file_path=csv_file)
    print(f"Data will be loaded from and saved to '{csv_file}'.")


    while True:
        display_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == '1':
            handle_create_account(banking_system)
        elif choice == '2':
            handle_deposit(banking_system)
        elif choice == '3':
            handle_withdraw(banking_system)
        elif choice == '4':
            handle_transfer(banking_system)
        elif choice == '5':
            handle_view_account(banking_system)
        elif choice == '6':
            handle_list_accounts(banking_system)
        elif choice == '7':
            print("Exiting system. Saving data...")
            banking_system.save_to_csv()
            print("Data saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
