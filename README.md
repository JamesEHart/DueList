# DueList

A command-line assignment and deadline tracker built for students. Add your assignments, mark them done, and sync a color-coded summary to Google Sheets you can check from anywhere.

---

## Features

- Add assignments with a title, class, and due date (natural language dates supported)
- List all assignments sorted by due date with color-coded status
- View only what's due in the next 7 days
- Mark assignments done or remove them
- Sync everything to a Google Sheet with automatic color coding
- Export a weekly summary as a formatted Word document
- Interactive REPL mode — run once and type commands without re-invoking Python

---

## Installation

**Requirements:** Python 3.9+

```bash
git clone https://github.com/your-username/DueList.git
cd DueList
pip install -r requirements.txt
```

---

## Usage

### Interactive mode (recommended)

```bash
python tracker.py
```

Drops you into a prompt where you type commands directly:

```
DueList
Type a command or 'help' or 'quit'
duelist> add "Calc homework" --class "Math" --due "June 20"
Added [1] "Calc homework" ... due 2026-06-20
duelist> list
duelist> done 1
duelist> quit
```

### One-off commands

You can also pass commands directly:

```bash
python tracker.py add "Essay draft" --class "English" --due "next Friday"
python tracker.py list
python tracker.py upcoming
python tracker.py done 2
python tracker.py remove 3
python tracker.py sync
python tracker.py export
```

---

## Commands

| Command | Description |
|---|---|
| `add "title" --class "Name" --due "date"` | Add a new assignment |
| `list` | Show all assignments sorted by due date |
| `upcoming` | Show assignments due within the next 7 days |
| `done <id>` | Mark an assignment as done |
| `remove <id>` | Delete an assignment |
| `export` | Export a weekly summary as a Word doc |
| `sync` | Push current state to Google Sheets |

**Due dates** accept natural language: `"June 20"`, `"next Friday"`, `"2026-06-20"`, `"tomorrow"`, etc.

---

## Terminal Color Coding

| Color | Meaning |
|---|---|
| Red | Overdue |
| Yellow | Due within 3 days |
| Green | Done |
| White | Upcoming (more than 3 days out) |

---

## Weekly Summary Export

Running `export` generates a `.docx` Word document with all your assignments organized into four sections:

- **Overdue** — past due and not done (red)
- **Due This Week** — due within the next 7 days (yellow)
- **Coming Up Later** — everything else pending
- **Completed** — finished assignments (green)

Each entry shows the assignment title, class, and due date. The file is saved to the project folder by default, named `DueList_Summary_YYYY-MM-DD.docx`. You can specify a custom path with `--output`:

```
duelist> export --output ~/Desktop/this_week.docx
```

---

## Google Sheets Sync

Syncing pushes all your assignments to a Google Sheet with the same color coding applied to rows.

### One-time setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project
2. Enable the **Google Sheets API** for that project
3. Create a **Service Account** under APIs & Services → Credentials
4. Download the service account key as JSON and save it as `credentials.json` in the project folder
5. Create a Google Sheet and share it with the service account's email address (found in `credentials.json` under `"client_email"`)
6. Run `python tracker.py sync` — you'll be prompted once to paste your Spreadsheet ID (the long string in the Sheet's URL). It saves to `config.json` so you won't be asked again.

### Sync output

The sheet gets a header row plus one row per assignment, sorted by due date. Row colors match the terminal color coding: red for overdue, yellow for due soon, green for done.

---

## Data Storage

Assignments are saved locally to `assignments.json` in the project folder. This file is excluded from git (see `.gitignore`) so your data stays on your machine.

---

## Features Coming Next

- **Priority levels** — tag assignments as low / medium / high priority
- **Recurring assignments** — set something to repeat weekly or by interval
- **Reminders** — desktop notification when a due date is approaching
- **Multiple subjects config** — predefine your class list so you don't have to type it each time

---

## Project Structure

```
DueList/
├── tracker.py        # CLI entry point and REPL
├── storage.py        # Local JSON read/write
├── sheets.py         # Google Sheets sync
├── export.py         # Word doc weekly summary
├── requirements.txt  # Python dependencies
└── assignments.json  # Your data (auto-created, git-ignored)
```
