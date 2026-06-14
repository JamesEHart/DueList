import argparse
import shlex
import sys
from datetime import date, timedelta

from dateutil import parser as dateparser

import storage
from sheets import sync_to_sheets

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


def _color(text, color_code):
    if not HAS_COLOR:
        return text
    return color_code + text + Style.RESET_ALL


def _status_color(assignment):
    if assignment["done"]:
        return Fore.GREEN
    today = date.today()
    due = date.fromisoformat(assignment["due"])
    if due < today:
        return Fore.RED
    if (due - today).days <= 3:
        return Fore.YELLOW
    return ""


def _print_table(assignments):
    if not assignments:
        print("No assignments found.")
        return

    header = f"{'ID':<4} {'Title':<30} {'Class':<15} {'Due':<12} {'Status'}"
    print(header)
    print("-" * len(header))

    for a in sorted(assignments, key=lambda x: x["due"]):
        status = "done" if a["done"] else "pending"
        row = f"{a['id']:<4} {a['title']:<30} {a['class']:<15} {a['due']:<12} {status}"
        color = _status_color(a)
        print(_color(row, color) if color else row)


def cmd_add(args):
    data = storage.load()
    try:
        due_dt = dateparser.parse(args.due)
        due_str = due_dt.date().isoformat()
    except (ValueError, OverflowError, TypeError):
        print(f"Could not parse due date: '{args.due}'")
        sys.exit(1)

    assignment = {
        "id": storage.next_id(data),
        "title": args.title,
        "class": args.cls,
        "due": due_str,
        "done": False,
        "added": date.today().isoformat(),
    }
    data["assignments"].append(assignment)
    storage.save(data)
    print(f"Added [{assignment['id']}] \"{assignment['title']}\" ... due {due_str}")


def cmd_list(args):
    data = storage.load()
    _print_table(data["assignments"])


def cmd_upcoming(args):
    data = storage.load()
    today = date.today()
    cutoff = today + timedelta(days=7)
    upcoming = [
        a for a in data["assignments"]
        if not a["done"] and today <= date.fromisoformat(a["due"]) <= cutoff
    ]
    if not upcoming:
        print("Nothing due in the next 7 days.")
    else:
        _print_table(upcoming)


def cmd_done(args):
    data = storage.load()
    for a in data["assignments"]:
        if a["id"] == args.id:
            a["done"] = True
            storage.save(data)
            print(f"Marked [{args.id}] \"{a['title']}\" as done.")
            return
    print(f"No assignment with id {args.id}.")


def cmd_remove(args):
    data = storage.load()
    before = len(data["assignments"])
    data["assignments"] = [a for a in data["assignments"] if a["id"] != args.id]
    if len(data["assignments"]) == before:
        print(f"No assignment with id {args.id}.")
        return
    storage.save(data)
    print(f"Removed assignment {args.id}.")


def cmd_sync(args):
    data = storage.load()
    sync_to_sheets(data, sheet_name=args.sheet)


def build_parser():
    parser = argparse.ArgumentParser(prog="duelist", description="DueList, assignment tracker")
    sub = parser.add_subparsers(dest="command", metavar="command")

    p_add = sub.add_parser("add", help="Add a new assignment")
    p_add.add_argument("title", help="Assignment title")
    p_add.add_argument("--class", dest="cls", required=True, metavar="CLASS", help="Course name")
    p_add.add_argument("--due", required=True, help="Due date (e.g. 'June 20', '2026-06-20')")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List all assignments")
    p_list.set_defaults(func=cmd_list)

    p_up = sub.add_parser("upcoming", help="Show assignments due in the next 7 days")
    p_up.set_defaults(func=cmd_upcoming)

    p_done = sub.add_parser("done", help="Mark an assignment as done")
    p_done.add_argument("id", type=int, help="Assignment ID")
    p_done.set_defaults(func=cmd_done)

    p_rm = sub.add_parser("remove", help="Remove an assignment")
    p_rm.add_argument("id", type=int, help="Assignment ID")
    p_rm.set_defaults(func=cmd_remove)

    p_sync = sub.add_parser("sync", help="Sync to Google Sheets")
    p_sync.add_argument("--sheet", default="DueList", help="Sheet tab name (default: DueList)")
    p_sync.set_defaults(func=cmd_sync)

    return parser


def run_repl(parser):
    print("DueList \nType a command or 'help' or 'quit'")
    while True:
        try:
            line = input("duelist> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            break
        if line == "help":
            parser.print_help()
            continue

        try:
            tokens = shlex.split(line)
        except ValueError as e:
            print(f"Parse error: {e}")
            continue

        try:
            args = parser.parse_args(tokens)
        except SystemExit:
            continue

        if not args.command:
            parser.print_help()
            continue

        args.func(args)


def main():
    parser = build_parser()

    if len(sys.argv) == 1:
        run_repl(parser)
    else:
        parser.required = True
        args = parser.parse_args()
        if not args.command:
            parser.print_help()
            sys.exit(1)
        args.func(args)


if __name__ == "__main__":
    main()
