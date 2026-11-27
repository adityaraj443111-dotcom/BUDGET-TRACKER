# ------------------------------------------------------------
# Personal Budget Tracker (simple console project)
# Modules:
#   1. Income and Expenditure records
#   2. Expense categorization
#   3. Budget and comparison
#   4. Monthly report
#   5. Alert and notification
# ------------------------------------------------------------

import json
import os
from datetime import date

FILE_NAME = "data.json"

# All data is kept in one dictionary so it is easy to save/load
data = {
    "transactions": [],   # list of dictionaries
    "categories": ["Food", "Travel", "Bills", "Shopping", "Other"],
    "budget": 0           # monthly budget set by the user
}


# ---------------- File handling ----------------
def load_data():
    """Load saved data from the file (if it exists)."""
    global data
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            data = json.load(f)


def save_data():
    """Save data to the file."""
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- Helper functions ----------------
def get_number(message):
    """Keep asking until the user enters a valid positive number."""
    while True:
        try:
            value = float(input(message))
            if value > 0:
                return value
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Invalid input! Enter a number.")


def choose_category():
    """Show categories and let the user pick one."""
    print("\nCategories:")
    for i, cat in enumerate(data["categories"], start=1):
        print(f"  {i}. {cat}")
    while True:
        try:
            choice = int(input("Choose category number: "))
            if 1 <= choice <= len(data["categories"]):
                return data["categories"][choice - 1]
        except ValueError:
            pass
        print("Invalid choice, try again.")


def current_month():
    """Returns the current month like '2026-11'."""
    return date.today().strftime("%Y-%m")


def month_totals(month):
    """Return (total_income, total_expense) for a given month."""
    income = 0
    expense = 0
    for t in data["transactions"]:
        if t["date"].startswith(month):
            if t["type"] == "income":
                income += t["amount"]
            else:
                expense += t["amount"]
    return income, expense


# ---------------- Module 1: Income and Expenditure ----------------
def add_income():
    amount = get_number("Enter income amount: ")
    note = input("Source (e.g. salary, pocket money): ")
    data["transactions"].append({
        "type": "income",
        "amount": amount,
        "category": "Income",
        "note": note,
        "date": str(date.today())
    })
    save_data()
    print("Income added!")


def add_expense():
    amount = get_number("Enter expense amount: ")
    category = choose_category()          # Module 2 is used here
    note = input("Note (what did you buy?): ")
    data["transactions"].append({
        "type": "expense",
        "amount": amount,
        "category": category,
        "note": note,
        "date": str(date.today())
    })
    save_data()
    print("Expense added!")
    check_alert()                         # Module 5 is used here


def view_transactions():
    if len(data["transactions"]) == 0:
        print("No transactions yet.")
        return
    print("\nNo.  Date        Type      Category    Amount    Note")
    print("-" * 60)
    for i, t in enumerate(data["transactions"], start=1):
        print(f"{i:<4} {t['date']}  {t['type']:<8}  {t['category']:<10}  "
              f"{t['amount']:<8}  {t['note']}")


# ---------------- Module 2: Expense categorization ----------------
def add_category():
    name = input("Enter new category name: ").strip().title()
    if name == "":
        print("Name cannot be empty.")
    elif name in data["categories"]:
        print("Category already exists.")
    else:
        data["categories"].append(name)
        save_data()
        print("Category added!")


def edit_transaction_category():
    """Manual editing of a category for an old expense."""
    view_transactions()
    if len(data["transactions"]) == 0:
        return
    try:
        num = int(input("Enter transaction number to edit: "))
        t = data["transactions"][num - 1]
    except (ValueError, IndexError):
        print("Invalid transaction number.")
        return
    if t["type"] != "expense":
        print("Only expenses have categories.")
        return
    t["category"] = choose_category()
    save_data()
    print("Category updated!")


# ---------------- Module 3: Budget and comparison ----------------
def set_budget():
    data["budget"] = get_number("Enter your monthly budget: ")
    save_data()
    print("Budget saved!")


def compare_budget():
    month = current_month()
    income, expense = month_totals(month)
    budget = data["budget"]

    if budget == 0:
        print("Please set a budget first (option 6).")
        return

    print("\n--- Budget vs Actual Spending ---")
    print("Budget        :", budget)
    print("Actual spent  :", expense)
    difference = budget - expense
    if difference >= 0:
        print("You are UNDER budget by", difference)
    else:
        print("You are OVER budget by", abs(difference))


# ---------------- Module 4: Monthly report ----------------
def monthly_report():
    month = input("Enter month (YYYY-MM) or press Enter for current month: ")
    if month == "":
        month = current_month()

    income, expense = month_totals(month)
    balance = income - expense

    print("\n========== Report for", month, "==========")
    print("Total Income   :", income)
    print("Total Expenses :", expense)
    print("Remaining      :", balance)

    # Category-wise spending
    print("\nSpending by category:")
    found = False
    for cat in data["categories"]:
        total = 0
        for t in data["transactions"]:
            if t["date"].startswith(month) and t["type"] == "expense" \
                    and t["category"] == cat:
                total += t["amount"]
        if total > 0:
            print(f"  {cat:<10}: {total}")
            found = True
    if not found:
        print("  No expenses this month.")


# ---------------- Module 5: Alert and notification ----------------
def check_alert():
    budget = data["budget"]
    if budget == 0:
        return
    _, expense = month_totals(current_month())
    percent = (expense / budget) * 100

    if percent >= 100:
        print("\n!!! ALERT: You have EXCEEDED your budget! !!!")
        give_suggestions()
    elif percent >= 80:
        print(f"\nWARNING: You have used {percent:.0f}% of your budget.")
        give_suggestions()


def give_suggestions():
    """Find the category with the highest spending and suggest saving."""
    month = current_month()
    highest_cat = ""
    highest_amount = 0
    for cat in data["categories"]:
        total = 0
        for t in data["transactions"]:
            if t["date"].startswith(month) and t["type"] == "expense" \
                    and t["category"] == cat:
                total += t["amount"]
        if total > highest_amount:
            highest_amount = total
            highest_cat = cat

    print("Saving suggestions:")
    if highest_cat != "":
        print(f"  - You spent the most on {highest_cat} ({highest_amount}). "
              f"Try to reduce it.")
    print("  - Avoid unnecessary shopping this month.")
    print("  - Track small daily expenses, they add up.")
    print("  - Try to save at least 10-20% of your income.")


# ---------------- Main menu ----------------
def main():
    load_data()
    while True:
        print("\n===== PERSONAL BUDGET TRACKER =====")
        print("1. Add income")
        print("2. Add expense")
        print("3. View all transactions")
        print("4. Add new category")
        print("5. Edit category of an expense")
        print("6. Set monthly budget")
        print("7. Compare budget with spending")
        print("8. Monthly report")
        print("9. Check alerts")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_income()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            view_transactions()
        elif choice == "4":
            add_category()
        elif choice == "5":
            edit_transaction_category()
        elif choice == "6":
            set_budget()
        elif choice == "7":
            compare_budget()
        elif choice == "8":
            monthly_report()
        elif choice == "9":
            check_alert()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


main()
