from decimal import Decimal

from django.db.models import Sum

from main.models import Attendance, PayrollItem


def calculate_payroll(employee, pay_period, payroll_items=None):
    """
    Calculate payroll for one employee for a specific month.

    OT is counted only when attendance status is Present.
    """

    # Get the selected month's date range
    month_start = pay_period.replace(day=1)

    if month_start.month == 12:
        month_end = month_start.replace(
            year=month_start.year + 1,
            month=1,
            day=1,
        )
    else:
        month_end = month_start.replace(
            month=month_start.month + 1,
            day=1,
        )

    # Sum OT hours only from Present attendance records
    ot_hours = Attendance.objects.filter(
        employee=employee,
        date__gte=month_start,
        date__lt=month_end,
        status=Attendance.StatusChoices.PRESENT,
    ).aggregate(
        total=Sum("ot_hours")
    )["total"] or Decimal("0.00")

    # Use the employee's position OT rate
    ot_rate = employee.position.ot_rate
    ot_amount = ot_hours * ot_rate

    # Use the employee's current basic salary when calculating
    basic_salary = employee.position.basic_salary

    # Calculate bonuses, allowances, deductions, and tax
    bonus = Decimal("0.00")
    allowance = Decimal("0.00")
    deduction = Decimal("0.00")
    tax = Decimal("0.00")

    for item in payroll_items or []:
        if item["type"] == PayrollItem.ItemTypeChoices.BONUS:
            bonus += item["amount"]
        elif item["type"] == PayrollItem.ItemTypeChoices.ALLOWANCE:
            allowance += item["amount"]
        elif item["type"] == PayrollItem.ItemTypeChoices.DEDUCTION:
            deduction += item["amount"]
        elif item["type"] == PayrollItem.ItemTypeChoices.TAX:
            tax += item["amount"]

    net_salary = (
        basic_salary
        + ot_amount
        + bonus
        + allowance
        - deduction
        - tax
    )

    return {
        "basic_salary": basic_salary,
        "ot_amount": ot_amount,
        "net_salary": net_salary,
        "ot_hours": ot_hours,
    }
