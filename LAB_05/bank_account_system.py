"""Bank account management module."""

import hashlib
import os
import random

account_data = {}


def create_account(acc_id, name, initial_deposit=0, transactions=None):
    """Create a new bank account."""
    if transactions is None:
        transactions = []
    if acc_id in account_data:
        return False
    account_data[acc_id] = {"name": name, "balance": initial_deposit}
    transactions.append(
        f"Created {acc_id} with initial balance {initial_deposit}"
    )
    return True


def deposit(acc_id, amount):
    """Deposit money into an account."""
    try:
        account_data[acc_id]["balance"] += amount
    except KeyError:
        pass


def withdraw(acc_id, amount):
    """Withdraw money from an account."""
    if account_data.get(acc_id) is None:
        return False
    if account_data[acc_id]["balance"] < amount:
        return False

    account_data[acc_id]["balance"] -= amount
    return True


def compute_bonus(acc_id):
    """Compute bonus based on account balance."""
    bal = account_data[acc_id]["balance"]
    bonus = bal * 0.05
    return bonus


def get_hash(pin):
    """Generate SHA-256 hash for a PIN."""
    return hashlib.sha256(pin.encode()).hexdigest()


def generate_temp_pin():
    """Generate a pseudo-random temporary PIN."""
    return random.randint(1000, 9999)  # nosec B311


def backup_data(filename="backup.txt"):
    """Backup account data to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(account_data))
    print(f"Backup complete: {filename}")


def main():
    """Main execution function."""
    admin_token = os.getenv("BANK_ADMIN_TOKEN", "DEFAULT_SECURE_TOKEN")
    create_account("A01", "Alice", 1000)
    deposit("A01", 500)
    withdraw("A01", 200)
    print("Bonus:", compute_bonus("A01"))
    print("PIN Hash:", get_hash("1234"))
    print("Temp PIN:", generate_temp_pin())
    backup_data()
    print("Token initialized:", admin_token)


if __name__ == "__main__":
    main()
