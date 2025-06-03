import decimal

# Set precision for decimal calculations (2 decimal places)
decimal.getcontext().prec = 28
TWO_PLACES = decimal.Decimal('0.01')

class Account:
    """
    Represents a single bank account.
    Manages account details and operations like deposit and withdrawal.
    """

    def __init__(self, account_number: str, name: str, initial_balance: decimal.Decimal = decimal.Decimal('0.00')):
        """
        Initializes a new Account

        Args:
            account_number (str): The unique identifier for the account
            name (str): The name of the account holder
            initial_balance (Decimal, optional): The starting balance. Defaults to Decimal('0.00')

        Raises:
            ValueError: If the initial balance is negative
            TypeError: If initial_balance is not a Decimal
        """
        if not isinstance(initial_balance, decimal.Decimal):
            raise TypeError("Initial balance must be a Decimal value.")
        if initial_balance < decimal.Decimal('0.00'):
            raise ValueError("Initial balance cannot be negative.")
        if not name or not isinstance(name, str):
            raise ValueError("Account holder name must be a non-empty string.")
        if not account_number or not isinstance(account_number, str):
            raise ValueError("Account number must be a non-empty string.")

        self._account_number: str = account_number
        self._name: str = name
        self._balance: decimal.Decimal = initial_balance.quantize(TWO_PLACES)

    def deposit(self, amount: decimal.Decimal) -> None:
        """
        Deposits a specified amount into the account

        Args:
            amount (Decimal): The amount to deposit

        Raises:
            ValueError: If the deposit amount is not positive
            TypeError: If amount is not a Decimal
        """
        if not isinstance(amount, decimal.Decimal):
            raise TypeError("Deposit amount must be a Decimal value.")
        if amount <= decimal.Decimal('0.00'):
            raise ValueError("Deposit amount must be positive.")

        self._balance += amount
        self._balance = self._balance.quantize(TWO_PLACES)

    def withdraw(self, amount: decimal.Decimal) -> None:
        """
        Withdraws a specified amount from the account
        Prevents overdraft

        Args:
            amount (Decimal): The amount to withdraw

        Raises:
            ValueError: If the withdrawal amount is not positive or if funds are insufficient
            TypeError: If amount is not a Decimal
        """
        if not isinstance(amount, decimal.Decimal):
            raise TypeError("Withdrawal amount must be a Decimal value.")
        if amount <= decimal.Decimal('0.00'):
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self._balance:
            raise ValueError("Insufficient funds for this withdrawal.")

        self._balance -= amount
        self._balance = self._balance.quantize(TWO_PLACES)

    def get_balance(self) -> decimal.Decimal:
        # Get the current account balance
        return self._balance.quantize(TWO_PLACES)

    def get_account_holder_name(self) -> str:
        # Get the name of the account holder
        return self._name

    def get_account_number(self) -> str:
        # Get the account number
        return self._account_number

    def __str__(self) -> str:
        # Get a string representation of the account
        return (f"Account Number: {self._account_number}, "
                f"Holder: {self._name}, "
                f"Balance: {self._balance:.2f}")