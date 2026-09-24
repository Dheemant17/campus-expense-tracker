import json 
import os
from datetime import date

DATA_FILE = "expenses_data.json"  # gets created in the same folder you run this from

# keeping categories fixed so the summary doesn't end up with "food", "Food", "FOOD" etc as 3 different rows
CATEGORIES = ["Food", "Hostel/Rent", "Transport", "Books/Stationery", "Entertainment", "Other"]

MAX_BAR = 30  # how long the longest bar in the chart gets, in characters


def load_data():
    # if there's no save file yet (first run), just start empty instead of crashing
    if not os.path.exists(DATA_FILE):
        return {"expenses": [], "budget": None}
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        print("hmm, couldn't read the save file properly, starting fresh")
        return {"expenses": [], "budget": None}
    # in case an old save file is missing a key
    if "expenses" not in data:
        data["expenses"] = []
    if "budget" not in data:
        data["budget"] = None
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def ask_amount(msg="Amount spent (Rs.): "):
    # loops till we get an actual positive number, no way around it
    while True:
        raw = input(msg).strip()
        try:
            val = float(raw)
        except ValueError:
            print("  that's not a number, try again (like 150 or 99.5)")
            continue
        if val <= 0:
            print("  needs to be more than 0")
            continue
        return round(val, 2)


def ask_category():
    print("  Category:")
    for i, c in enumerate(CATEGORIES, 1):
        print(f"    {i}. {c}")
    while True:
        raw = input(f"  pick 1-{len(CATEGORIES)}: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(CATEGORIES):
            return CATEGORIES[int(raw) - 1]
        print("  not a valid option, try again")


# ---- adding + managing expenses ----

def add_expense(data):
    print("\nAdding a new expense")
    amt = ask_amount()
    cat = ask_category()
    note = input("  note (optional): ").strip()

    # ids just count up from whatever the highest one so far is
    used_ids = [e["id"] for e in data["expenses"]]
    new_id = max(used_ids, default=0) + 1

    data["expenses"].append({
        "id": new_id,
        "date": date.today().isoformat(),
        "category": cat,
        "amount": amt,
        "note": note,
    })
    save_data(data)
    print(f"  saved #{new_id} - Rs.{amt:.2f} on {cat}")


def set_budget(data):
    print("\nMonthly budget")
    if data.get("budget"):
        print(f"  currently set to Rs.{data['budget']:.2f}")
    amt = ask_amount("  new monthly budget (0 to clear it): ")
    if amt == 0:
        data["budget"] = None
        print("  budget cleared")
    else:
        data["budget"] = amt
        print("  updated")
    save_data(data)


def delete_expense(data):
    if not data["expenses"]:
        print("\nnothing to delete, list's empty")
        return
    show_all(data)
    raw = input("\nid to delete (blank = cancel): ").strip()
    if raw == "":
        return
    if not raw.isdigit():
        print("  that's not an id")
        return
    wanted = int(raw)
    new_list = [e for e in data["expenses"] if e["id"] != wanted]
    if len(new_list) == len(data["expenses"]):
        print(f"  couldn't find #{wanted}")
        return
    data["expenses"] = new_list
    save_data(data)
    print(f"  deleted #{wanted}")


# ---- turning the saved list into numbers worth showing ----

def get_totals(data):
    expenses = data["expenses"]
    total = 0
    by_cat = {}
    for c in CATEGORIES:
        by_cat[c] = 0.0

    for e in expenses:
        total += e["amount"]
        cat = e.get("category", "Other")
        by_cat[cat] = by_cat.get(cat, 0.0) + e["amount"]

    count = len(expenses)
    avg = total / count if count else 0

    top_cat = None
    if total > 0:
        top_cat = max(by_cat, key=by_cat.get)

    this_month = date.today().strftime("%Y-%m")
    month_total = sum(e["amount"] for e in expenses if e["date"].startswith(this_month))

    return {
        "total": total,
        "count": count,
        "avg": avg,
        "by_cat": by_cat,
        "top_cat": top_cat,
        "month_total": month_total,
        "budget": data.get("budget"),
    }


def show_summary(data):
    print("\n----- SUMMARY -----")
    t = get_totals(data)

    if t["count"] == 0:
        print("no expenses logged yet, add one from the menu")
        return

    print(f"Total spent      : Rs.{t['total']:.2f}")
    print(f"Transactions     : {t['count']}")
    print(f"Average          : Rs.{t['avg']:.2f}")
    print(f"Top category     : {t['top_cat']}")
    print(f"This month       : Rs.{t['month_total']:.2f}")

    if t["budget"]:
        left = t["budget"] - t["month_total"]
        used_pct = (t["month_total"] / t["budget"]) * 100
        if left < 0:
            print(f"Budget           : Rs.{t['budget']:.2f}  -> OVER by Rs.{abs(left):.2f} ({used_pct:.0f}% used)")
        else:
            print(f"Budget           : Rs.{t['budget']:.2f}  -> {used_pct:.0f}% used, Rs.{left:.2f} left")

    print("\nBy category:")
    highest = max(t["by_cat"].values())
    if highest == 0:
        highest = 1  # so we don't divide by zero below
    # sort so the biggest spending category shows up first
    sorted_cats = sorted(t["by_cat"].items(), key=lambda pair: pair[1], reverse=True)
    for cat, amt in sorted_cats:
        if amt == 0:
            continue
        bar_len = int((amt / highest) * MAX_BAR)
        pct = (amt / t["total"]) * 100
        print(f"  {cat:<17} Rs.{amt:>8.2f}  {pct:4.1f}%  {'#' * bar_len}")


def show_all(data):
    print("\n----- ALL EXPENSES -----")
    if not data["expenses"]:
        print("(nothing here yet)")
        return
    print(f"{'id':<4}{'date':<12}{'category':<18}{'amount':>9}   note")
    for e in sorted(data["expenses"], key=lambda x: x["date"]):
        print(f"{e['id']:<4}{e['date']:<12}{e['category']:<18}{e['amount']:>9.2f}   {e.get('note','')}")


def main():
    data = load_data()
    print(f"loaded {len(data['expenses'])} expense(s) from before")

    while True:
        print("""
1. Add expense
2. Summary
3. View all
4. Delete an expense
5. Set budget
6. Quit""")
        choice = input("choice: ").strip()

        if choice == "1":
            add_expense(data)
        elif choice == "2":
            show_summary(data)
        elif choice == "3":
            show_all(data)
        elif choice == "4":
            delete_expense(data)
        elif choice == "5":
            set_budget(data)
        elif choice == "6":
            print(f"saved everything to {DATA_FILE}, bye!")
            break
        else:
            print("pick a number 1-6")


if __name__ == "__main__":
    main()
