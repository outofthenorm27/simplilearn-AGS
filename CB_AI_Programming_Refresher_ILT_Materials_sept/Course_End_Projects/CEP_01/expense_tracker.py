"""
Personal Expense Tracker (CLI)
--------------------------------
A beginner-friendly Python application that teaches core Python basics *while*
building something useful.

Covers:
- Data Types & Assignment (lists, dicts, tuples, floats, ints, bools, strings)
- Operators in Python (arithmetic, comparison, logical, augmented assignment)
- Strings in Python (strip, lower, upper, title, f-strings, join)
- File Handling (CSV read/write, exists checks, context managers)
- Error Handling (try/except/else/finally, custom exceptions, input validation)

How to run:
    python expense_tracker.py

Files used/created:
    expenses.csv   -> persistent expense store
    budget.txt     -> optional (stores last monthly budget set by the user)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# ===========================
# Constants & File Resources
# ===========================

APP_DIR = Path(".")
EXPENSES_FILE = APP_DIR / "expenses.csv"
BUDGET_FILE = APP_DIR / "budget.txt"

DATE_FMT = "%Y-%m-%d"  # YYYY-MM-DD

# ===========================
# Data Models
# ===========================

@dataclass
class Expense:
    date: str          # stored as 'YYYY-MM-DD' string for simplicity
    category: str
    amount: float
    description: str

    @staticmethod
    def validate_date(date_str: str) -> str:
        """Validate and normalize the date string. Raises ValueError if invalid."""
        try:
            # Using datetime both validates and lets us normalize the format.
            dt = datetime.strptime(date_str.strip(), DATE_FMT)
            return dt.strftime(DATE_FMT)
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    @staticmethod
    def from_user_input() -> "Expense":
        """Create an Expense from interactive user input with validations.

        Demonstrates:
            - input() for strings (Strings in Python)
            - .strip() for cleanup
            - type conversion (float)
            - try/except for validation (Error Handling)
        """
        date_raw = input("Enter date (YYYY-MM-DD): ").strip()
        date_ok = Expense.validate_date(date_raw)

        category = input("Enter category (e.g., Food, Travel): ").strip().title()
        if not category:
            raise ValueError("Category cannot be empty.")

        amount_raw = input("Enter amount (e.g., 12.50): ").strip()
        try:
            amount = float(amount_raw)
        except ValueError:
            raise ValueError("Amount must be a valid number.")
        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        description = input("Enter a brief description: ").strip()
        if not description:
            raise ValueError("Description cannot be empty.")

        return Expense(date=date_ok, category=category, amount=amount, description=description)

# ===========================
# Storage Layer
# ===========================

def load_expenses(file_path: Path = EXPENSES_FILE) -> List[Expense]:
    """Load expenses from a CSV file if it exists.

    Demonstrates:
        - File Handling (checking Path.exists, opening files, CSV reader)
        - Error Handling (catching IO/CSV errors and continuing safely)
    """
    expenses: List[Expense] = []
    if not file_path.exists():
        return expenses

    try:
        with file_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validate required fields and types
                try:
                    date = Expense.validate_date(row.get("date", "").strip())
                    category = row.get("category", "").strip().title()
                    amount = float(row.get("amount", "0").strip())
                    description = row.get("description", "").strip()
                    if not (date and category and description):
                        # If incomplete, skip (requirement from the spec)
                        print("Skipping incomplete record found in file.")
                        continue
                    if amount < 0:
                        print("Skipping record with negative amount found in file.")
                        continue
                    expenses.append(Expense(date, category, amount, description))
                except Exception as e:
                    print(f"Skipping a malformed row due to error: {e}")
    except FileNotFoundError:
        # Already handled by exists check; shown for teaching purposes
        pass
    except Exception as e:
        print(f"Error loading expenses: {e}")
    return expenses


def save_expenses(expenses: List[Expense], file_path: Path = EXPENSES_FILE) -> None:
    """Save expenses to a CSV file.

    Demonstrates:
        - File Handling (create file if missing, CSV writer, newline handling)
        - Error Handling around IO
    """
    try:
        with file_path.open("w", newline="", encoding="utf-8") as f:
            fieldnames = ["date", "category", "amount", "description"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for exp in expenses:
                writer.writerow(asdict(exp))
        print(f"Saved {len(expenses)} expense(s) to {file_path}.")
    except Exception as e:
        print(f"Error saving expenses: {e}")


def load_budget(file_path: Path = BUDGET_FILE) -> Optional[float]:
    """Optionally load the last saved monthly budget from a text file."""
    if not file_path.exists():
        return None
    try:
        val = file_path.read_text(encoding="utf-8").strip()
        return float(val) if val else None
    except Exception:
        return None


def save_budget(budget: float, file_path: Path = BUDGET_FILE) -> None:
    """Persist the current monthly budget to a text file."""
    try:
        file_path.write_text(f"{budget}", encoding="utf-8")
    except Exception as e:
        print(f"Warning: couldn't save budget to disk ({e}).")

# ===========================
# Budget & Reporting
# ===========================

def total_spent(expenses: List[Expense]) -> float:
    """Compute the total amount spent using arithmetic operators.

    Demonstrates:
        - Arithmetic Operators (+, +=)
        - Iteration over a list of dataclass instances
    """
    total = 0.0
    for e in expenses:
        total += e.amount  # augmented assignment operator
    return round(total, 2)


def total_by_category(expenses: List[Expense]) -> Dict[str, float]:
    """Compute totals by category to show dictionary usage and operators."""
    totals: Dict[str, float] = {}
    for e in expenses:
        key = e.category
        if key not in totals:
            totals[key] = 0.0
        totals[key] += e.amount
    # Optionally round values for display
    return {k: round(v, 2) for k, v in totals.items()}


def track_budget(expenses: List[Expense], current_budget: Optional[float]) -> Optional[float]:
    """Set or track the monthly budget against current expenses.

    Demonstrates:
        - Comparison Operators (>, >=, <, <=, ==, !=)
        - Logical Operators (and, or, not)
        - Strings (f-strings)
    """
    if current_budget is None:
        print("No monthly budget set yet.")
        ans = input("Would you like to set one now? (y/n): ").strip().lower()
        if ans == "y":
            while True:
                raw = input("Enter your monthly budget amount: ").strip()
                try:
                    budget = float(raw)
                    if budget < 0:
                        print("Budget cannot be negative. Try again.")
                        continue
                    save_budget(budget)
                    current_budget = budget
                    print(f"Budget saved: ${budget:.2f}")
                    break
                except ValueError:
                    print("Please enter a valid number.")
        else:
            print("Okay, you can set a budget later from the menu.")
            return None

    # Show current status
    spent = total_spent(expenses)
    remaining = (current_budget or 0.0) - spent

    # Comparison operator demo
    if spent > (current_budget or 0.0):
        print(f"⚠️ You have exceeded your budget by ${abs(remaining):.2f}!")
    else:
        print(f"✅ Within budget. Remaining: ${remaining:.2f}")

    # Category breakdown for learning
    cat = total_by_category(expenses)
    if cat:
        print("\nSpending by category:")
        for c, amt in sorted(cat.items(), key=lambda x: (-x[1], x[0])):
            print(f"  - {c}: ${amt:.2f}")
    else:
        print("No spending yet to break down by category.")
    return current_budget

# ===========================
# Display & Validation
# ===========================

def display_expenses(expenses: List[Expense]) -> None:
    """Print a table-like view of expenses.

    Demonstrates:
        - Looping and formatted strings
        - Basic "validation before display" (skip incomplete records)
    """
    if not expenses:
        print("No expenses to show yet.")
        return

    # Header
    print("\nYour Expenses:")
    print("-" * 70)
    print(f"{'Date':<12} {'Category':<15} {'Amount':>10}   Description")
    print("-" * 70)

    shown = 0
    for e in expenses:
        # Minimal validation before display (already validated on input / load)
        if not (e.date and e.category and e.description and isinstance(e.amount, (int, float))):
            print("Skipping an incomplete or invalid entry at display time.")
            continue
        print(f"{e.date:<12} {e.category:<15} {e.amount:>10.2f}   {e.description}")
        shown += 1

    print("-" * 70)
    print(f"Total shown: {shown}   |   Total spent: ${total_spent(expenses):.2f}\n")


def add_expense_flow(expenses: List[Expense]) -> None:
    """Interactive flow to add an expense with robust error handling."""
    try:
        new_expense = Expense.from_user_input()
    except ValueError as ve:
        print(f"Input error: {ve}")
        return
    except Exception as e:
        print(f"Unexpected error while adding expense: {e}")
        return

    # Example of operator and string usage
    msg = f"Add {new_expense.category} expense of ${new_expense.amount:.2f} on {new_expense.date}? (y/n): "
    confirm = input(msg).strip().lower()
    if confirm == "y":
        expenses.append(new_expense)
        print("Expense added!")
    else:
        print("Cancelled adding expense.")

# ===========================
# Interactive Menu
# ===========================

def show_menu() -> None:
    """Display the interactive menu.

    Demonstrates:
        - Strings & printing
        - Multi-line strings
    """
    menu = """
========== Personal Expense Tracker ==========
1) Add expense
2) View expenses
3) Set/Track budget
4) Save expenses
5) Exit (auto-save)
==============================================
"""
    print(menu)


def main() -> None:
    print("Loading saved expenses (if any)...")
    expenses = load_expenses()
    budget = load_budget()

    # Quick intro for students
    print(
        "Welcome! This app demonstrates Python basics while helping you track spending.\n"
        "You'll practice data types, operators, strings, file handling, and error handling as you use it.\n"
    )

    while True:
        try:
            show_menu()
            choice = input("Choose an option (1-5): ").strip()

            # Comparison operators and logical operators in action
            if choice == "1":
                add_expense_flow(expenses)
            elif choice == "2":
                display_expenses(expenses)
            elif choice == "3":
                budget = track_budget(expenses, budget)
            elif choice == "4":
                save_expenses(expenses)
            elif choice == "5":
                # Auto-save on exit to be user-friendly
                save_expenses(expenses)
                print("Goodbye!")
                break
            else:
                print("Please choose a valid option (1-5).")

        except KeyboardInterrupt:
            print("\nDetected Ctrl+C. Exiting safely...")
            save_expenses(expenses)
            break
        except Exception as e:
            # Catch-all to prevent crashes; also a teaching moment.
            print(f"An unexpected error occurred: {e}")
            # Loop continues so the user doesn't lose progress.

if __name__ == "__main__":
    main()
