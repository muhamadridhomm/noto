"""Generic spreadsheet and HTML exports for user-created notes and planning items."""
from datetime import date, datetime
from html import escape
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


def calculate_relative_days(due_date_str: str, done: bool = False) -> str:
    if not due_date_str:
        return "No date"
    if done:
        return f"Done ({due_date_str})"
    try:
        target = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
        days = (target - date.today()).days
        return "Due today" if days == 0 else ("Overdue" if days < 0 else f"{days} days left")
    except (TypeError, ValueError):
        return str(due_date_str)


def generate_excel_export(tasks: list, targets: list, title: str = "Noto planning export") -> bytes:
    workbook = Workbook()
    task_sheet = workbook.active
    task_sheet.title = "Tasks"
    task_headers = ["Status", "Task", "Group", "Priority", "Due date", "Timing", "Notes"]
    task_sheet.append(task_headers)
    for cell in task_sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="334155")
    for task in tasks:
        task_sheet.append([
            task.get("status", "To Do"), task.get("title", ""), task.get("group") or "",
            task.get("priority", "Normal"), task.get("due_date") or "",
            calculate_relative_days(task.get("due_date", ""), bool(task.get("done"))),
            task.get("notes") or "",
        ])
    for col, width in enumerate([16, 42, 28, 14, 16, 18, 56], 1):
        task_sheet.column_dimensions[get_column_letter(col)].width = width
    task_sheet.freeze_panes = "A2"
    task_sheet.auto_filter.ref = task_sheet.dimensions
    for row in task_sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    target_sheet = workbook.create_sheet("Milestones")
    target_headers = ["Milestone", "Category", "Due date", "Description"]
    target_sheet.append(target_headers)
    for cell in target_sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="0F766E")
    for target in targets:
        target_sheet.append([
            target.get("title", ""), target.get("badge") or "Milestone",
            target.get("date") or "", target.get("description") or "",
        ])
    for col, width in enumerate([42, 20, 16, 60], 1):
        target_sheet.column_dimensions[get_column_letter(col)].width = width
    target_sheet.freeze_panes = "A2"
    target_sheet.auto_filter.ref = target_sheet.dimensions
    for row in target_sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def generate_html_export(tasks: list, targets: list, title: str = "Noto planning export") -> str:
    safe_title = escape(title)
    def table(headers, rows):
        head = "".join(f"<th>{escape(str(value))}</th>" for value in headers)
        body = "".join("<tr>" + "".join(f"<td>{escape(str(value or ''))}</td>" for value in row) + "</tr>" for row in rows)
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
    task_rows = [[t.get("status", "To Do"), t.get("title", ""), t.get("group") or "", t.get("priority", "Normal"), t.get("due_date") or "", t.get("notes") or ""] for t in tasks]
    milestone_rows = [[m.get("title", ""), m.get("badge") or "Milestone", m.get("date") or "", m.get("description") or ""] for m in targets]
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>""" + safe_title + """</title><style>body{font:15px system-ui,sans-serif;max-width:1100px;margin:40px auto;padding:0 20px;color:#1e293b}h1{color:#0f172a}h2{margin-top:36px}table{border-collapse:collapse;width:100%;margin:12px 0 28px}th,td{border:1px solid #cbd5e1;padding:8px;text-align:left;vertical-align:top}th{background:#e2e8f0}tr:nth-child(even){background:#f8fafc}</style><h1>""" + safe_title + """</h1><p>Exported from Noto.</p><h2>Tasks</h2>""" + table(["Status", "Task", "Group", "Priority", "Due date", "Notes"], task_rows) + "<h2>Milestones</h2>" + table(["Milestone", "Category", "Due date", "Description"], milestone_rows) + "</html>"
