from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def currency(value):
    if value in (None, ""):
        return "$0.00"

    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    return f"${amount:,.2f}"


@register.filter
def invoice_status_class(value):
    mapping = {
        "draft": "status-draft",
        "sent": "status-sent",
        "paid": "status-paid",
        "overdue": "status-overdue",
        "planning": "status-planning",
        "active": "status-active",
        "on_hold": "status-on-hold",
        "completed": "status-completed",
    }
    return mapping.get(value, "")
