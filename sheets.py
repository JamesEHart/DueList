import json
import os
import sys
from datetime import date

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def _load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def _save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return {"red": r / 255, "green": g / 255, "blue": b / 255}


def _row_color(assignment):
    if assignment["done"]:
        return "#6BCB77"
    today = date.today()
    due = date.fromisoformat(assignment["due"])
    if due < today:
        return "#FF6B6B"
    if (due - today).days <= 3:
        return "#FFD93D"
    return "#FFFFFF"


def sync_to_sheets(data, sheet_name="DueList"):
    if not os.path.exists(CREDENTIALS_FILE):
        print("credentials.json not found.")
        print("Set up a Google Cloud service account and place the key file at credentials.json.")
        print("Then share your Google Sheet with the service account email.")
        sys.exit(1)

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("Missing dependencies. Run: pip install gspread google-auth")
        sys.exit(1)

    config = _load_config()
    if "spreadsheet_id" not in config:
        spreadsheet_id = input("Enter your Google Spreadsheet ID (from the URL): ").strip()
        config["spreadsheet_id"] = spreadsheet_id
        _save_config(config)
    else:
        spreadsheet_id = config["spreadsheet_id"]

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    gc = gspread.authorize(creds)

    spreadsheet = gc.open_by_key(spreadsheet_id)

    try:
        ws = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=sheet_name, rows=200, cols=6)

    ws.clear()

    headers = ["ID", "Title", "Class", "Due Date", "Status", "Date Added"]
    rows = [headers]
    for a in sorted(data["assignments"], key=lambda x: x["due"]):
        rows.append([
            a["id"],
            a["title"],
            a["class"],
            a["due"],
            "Done" if a["done"] else "Pending",
            a["added"],
        ])

    ws.update("A1", rows)

    # Bold header row
    sheet_id = ws.id
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True},
                        "backgroundColor": _hex_to_rgb("#4A4E69"),
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)",
            }
        }
    ]

    # Color each data row
    for i, a in enumerate(sorted(data["assignments"], key=lambda x: x["due"]), start=1):
        color = _row_color(a)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": i,
                    "endRowIndex": i + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": _hex_to_rgb(color),
                    }
                },
                "fields": "userEnteredFormat.backgroundColor",
            }
        })

    spreadsheet.batch_update({"requests": requests})

    total = len(data["assignments"])
    print(f"Synced {total} assignment(s) to '{sheet_name}' in spreadsheet {spreadsheet_id}.")
