# Campus Expense Tracker (CLI)

My submission for the SNU GDG recruitment challenge. It's a command-line tool
for tracking daily campus spending - food, hostel, transport, books, whatever
- written in plain Python since that's the language I've actually learned so far.

## What it does

1. **Input** - it asks you for an amount, a category (pick from a list, no
   typos possible), and an optional note.
2. **Process/Store** - every entry gets saved into a JSON file
   (`expenses_data.json`) so it's still there next time you run the script.
   When you ask for the summary, it adds everything up by category, works
   out your top spending category, this month's total, and checks it
   against a budget if you've set one.
3. **Output** - prints all that back as a readable summary, plus a little
   text bar chart so you can see which category is eating your money
   without needing matplotlib or anything extra.

## Running it

Just needs Python 3, nothing to install:

```bash
python3 campus_expense_tracker.py
```

Follow the menu. Your data saves automatically into `expenses_data.json` in
the same folder - delete that file if you want to start over.

## Features

- Add expenses with validation (amount has to be a positive number, category
  picked from a fixed list)
- Data persists between runs (JSON file)
- Summary screen: total, count, average, top category, this month's spend
- Optional monthly budget with an over/under warning
- Category breakdown with a text bar chart
- View all expenses in a table
- Delete an expense by id

## Notes on how I built it

I split the "crunch the numbers" part (`get_totals`) from the "print stuff"
part (`show_summary`) on purpose - made it way easier to check the math was
right without staring at printed text. I actually ran a full fake session
through it (add a few expenses, set a budget, delete one, check the summary
again) and checked the totals by hand before trusting it.

One thing I had to think through: ids for each expense. If you just number
them by position in the list, deleting one and adding a new one can end up
reusing an id that used to belong to something else, which gets confusing.
So `add_expense` looks at the highest id currently in the file and adds 1
to that instead - new expenses never collide with a deleted one's old id.

Things I'd add if I kept going: exporting to CSV, and maybe tracking spend
by week instead of just "this month."
