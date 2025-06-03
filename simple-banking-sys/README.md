# Simple Banking System

A command-line based Simple Banking System written in Python. This system allows users to create accounts, deposit and withdraw funds, transfer money between accounts, and persists data to a CSV file.

## Features

* **Account Creation**: Users can create new bank accounts with a name and an initial balance.
* **Deposit**: Users can deposit money into their accounts.
* **Withdrawal**: Users can withdraw money from their accounts. Overdrafts are not allowed.
* **Transfer**: Users can transfer money to other accounts within the system.
* **View Account Details**: Users can view the details of a specific account.
* **List All Accounts**: Users can list all accounts currently in the system.
* **Data Persistence**: Account information and system state (like the next available account number) are saved to and loaded from a `bank_data.csv` file.
* **Precision Handling**: Uses Python's `Decimal` type for all monetary calculations to ensure accuracy.

## Project Structure

simple-banking-sys/  
├── account.py            # Defines the Account class for individual bank accounts.  
├── banking_system.py     # Defines the BankingSystem class to manage accounts and operations.  
├── main.py               # The main command-line interface (CLI) for user interaction.  
├── test_account.py       # Unit tests for the Account class.  
├── test_banking_system.py # Unit tests for the BankingSystem class.  
├── bank_data.csv         # (Generated at runtime) Stores account data.  
└── README.md             # This file.
## Prerequisites

* Python 3.7 or higher

## Setup and Running

1.  **Clone the Repository or Download Files**:
    ```bash
    git clone <repository-url>
    cd simple-banking-system
    ```
    Alternatively, ensure all Python files (`account.py`, `banking_system.py`, `main.py`, `test_account.py`, `test_banking_system.py`) are in the same directory.

2.  **Navigate to the Project Directory**:
    ```bash
    cd path/to/your/simple-banking-system
    ```

3.  **Run the Application**:
    ```bash
    python main.py
    ```
    The application will start, load any existing data from `bank_data.csv` (if it exists in the same directory), and present you with a menu of options.

4.  **Running Unit Tests (Optional)**:
    * To run all tests (discovery mode, recommended):
        ```bash
        python -m unittest discover
        ```
    * To run tests for a specific module:
        ```bash
        python -m unittest test_account.py
        python -m unittest test_banking_system.py
        ```

## Data Persistence

* The system automatically saves all account data and the next available account number to a file named `bank_data.csv` in the same directory as `main.py`.
* Saving occurs when the user chooses the "Exit" option from the main menu.
* Loading occurs automatically when `main.py` is started. If `bank_data.csv` does not exist, the system will start fresh.

## Code Quality and Principles

* **KISS**: The system is designed with simplicity in mind, avoiding unnecessary complexity.
* **Object-Oriented Design**: The system is structured using classes (`Account`, `BankingSystem`) to model real-world entities and operations.
* **Error Handling**: Basic error handling is implemented to manage invalid inputs and exceptional conditions (e.g., insufficient funds).
* **Test Coverage**: Unit tests are provided for core components to verify functionality and help maintain code quality.

