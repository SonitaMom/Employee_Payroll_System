import json
from datetime import datetime
from django.utils import timezone
from django.utils.timesince import timesince
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from main.models import Employee, Payroll, Payment, Attendance


def _format_time_ago(dt):
    """Format a datetime to a friendly string like '2 hours ago', '1 day ago', or 'Just now'."""
    if not dt:
        return "recently"
    now = timezone.now()
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    diff = now - dt
    if diff.total_seconds() < 60:
        return "Just now"
    since = timesince(dt, now).split(",")[0].strip().replace("\xa0", " ")
    return f"{since} ago"


def _clean_target_name(raw_text):
    """Clean representation names like '1 - Horn Sereyboth' to 'Horn Sereyboth'."""
    if not raw_text:
        return "record"
    raw_str = str(raw_text).strip()
    if " - " in raw_str:
        parts = raw_str.split(" - ", 1)
        if parts[0].strip().isdigit():
            return parts[1].strip()
    return raw_str


def get_recent_activities(limit=4):
    """
    Query the latest user activities (who, what, when).
    Primary source: Django's LogEntry (tracks admin/system user actions).
    Fallback source: Recent database records (Employee, Payroll, Payment, Attendance).
    """
    activities = []

    # 1. First attempt: Query LogEntry (tracks exact user, action, timestamp)
    log_entries = (
        LogEntry.objects.select_related("user", "content_type")
        .order_by("-action_time")[: limit * 2]
    )

    for entry in log_entries:
        model_name = entry.content_type.model.lower() if entry.content_type else ""
        target_name = _clean_target_name(entry.object_repr)
        user_display = entry.user.get_full_name() or entry.user.username or "Admin"

        icon = "bi-clock-history"
        icon_bg = "primary"  # primary | success | purple | orange

        if model_name == "employee":
            icon = "bi-person-fill"
            if entry.action_flag == ADDITION:
                title = "New employee added"
                description = f"{target_name} joined the company"
                icon_bg = "primary"
            elif entry.action_flag == DELETION:
                title = "Employee removed"
                description = f"{target_name} was removed"
                icon_bg = "orange"
            else:
                title = "Employee updated"
                description = f"{user_display} updated {target_name}"
                icon_bg = "primary"

        elif model_name == "payroll":
            icon = "bi-wallet2"
            icon_bg = "purple"
            if entry.action_flag == ADDITION:
                title = "Payroll generated"
                description = f"{target_name}"
            elif entry.action_flag == DELETION:
                title = "Payroll deleted"
                description = f"{target_name}"
            else:
                title = "Payroll updated"
                description = f"{user_display} modified {target_name}"

        elif model_name == "payment":
            icon = "bi-credit-card-2-front-fill"
            icon_bg = "success"
            if entry.action_flag == ADDITION:
                title = "Payment completed"
                description = f"{target_name}"
            else:
                title = "Payment recorded"
                description = f"{target_name}"

        elif model_name == "attendance":
            icon = "bi-calendar-check"
            icon_bg = "orange"
            title = "Attendance logged"
            description = f"{target_name}"

        elif model_name in ["department", "position"]:
            icon = "bi-building" if model_name == "department" else "bi-briefcase-fill"
            icon_bg = "primary"
            verb = "added" if entry.action_flag == ADDITION else "updated"
            title = f"{model_name.capitalize()} {verb}"
            description = f"{user_display} {verb} {target_name}"

        else:
            action_verb = "added" if entry.action_flag == ADDITION else "changed"
            title = f"{entry.content_type.name.capitalize()} {action_verb}" if entry.content_type else "System action"
            description = f"{target_name}"
            icon_bg = "primary"

        activities.append({
            "title": title,
            "description": description,
            "user": user_display,
            "time_ago": _format_time_ago(entry.action_time),
            "timestamp": entry.action_time,
            "icon": icon,
            "icon_bg": icon_bg,
        })

        if len(activities) >= limit:
            break

    # 2. Fallback: If no LogEntry records exist, pull recent domain model items
    if len(activities) < limit:
        # Fallback employees
        for emp in Employee.objects.order_by("-created_at")[:limit]:
            activities.append({
                "title": "New employee added",
                "description": f"{emp.first_name} {emp.last_name} joined the company",
                "user": "System",
                "time_ago": _format_time_ago(emp.created_at),
                "timestamp": emp.created_at,
                "icon": "bi-person-fill",
                "icon_bg": "primary",
            })

    # Sort descending by timestamp and trim to limit
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]
