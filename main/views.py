from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from .models import *
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    return redirect("login")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


from main.services.dashboard import get_recent_activities


@login_required
@permission_required("main.view_dashboard", raise_exception=True)
def dashboard(request):
    now = timezone.now()
    total_employees = Employee.objects.count()
    employees_this_month = Employee.objects.filter(
        hire_date__year=now.year, hire_date__month=now.month
    ).count()

    total_payment = Payment.objects.filter(status=Payment.StatusChoices.COMPLETED).aggregate(Sum('amount'))['amount__sum'] or 0
    paid_count = Payment.objects.filter(status=Payment.StatusChoices.COMPLETED).count()
    pending_count = Payment.objects.filter(status=Payment.StatusChoices.PENDING).count()

    total_payment_count = paid_count + pending_count
    paid_percent = round((paid_count / total_payment_count) * 100) if total_payment_count > 0 else 0
    pending_percent = round((pending_count / total_payment_count) * 100) if total_payment_count > 0 else 0

    # Build last 6 months (chronological) with real DB payment amounts (0 if none)
    raw_payments = {
        item["month"].strftime("%Y-%m"): float(item["total"] or 0)
        for item in Payment.objects
        .filter(status=Payment.StatusChoices.COMPLETED, payment_date__isnull=False)
        .annotate(month=TruncMonth("payment_date"))
        .values("month")
        .annotate(total=Sum("amount"))
    }

    monthly_payment = []
    for i in reversed(range(6)):
        # Calculate month date going back i months
        m = (now.month - 1 - i) % 12 + 1
        y = now.year - ((now.month - 1 - i) // 12 * -1 if (now.month - 1 - i) < 0 else 0)
        key = f"{y:04d}-{m:02d}"
        from datetime import date
        month_label = date(y, m, 1).strftime("%b")
        monthly_payment.append({
            "month": month_label,
            "total": raw_payments.get(key, 0),
        })

    total_absent = Attendance.objects.filter(date=now.date(), status=Attendance.StatusChoices.ABSENT).count()
    total_present = Attendance.objects.filter(date=now.date(), status=Attendance.StatusChoices.PRESENT).count()
    total_leave = Attendance.objects.filter(date=now.date(), status=Attendance.StatusChoices.LEAVE).count()
    total_ot_hours = Attendance.objects.filter(date=now.date()).aggregate(Sum('ot_hours'))['ot_hours__sum'] or 0

    # Query 4 latest user activities from main.services.dashboard
    recent_activities = get_recent_activities(limit=4)

    current_month_name = now.strftime("%B %Y")

    return render(request, "dashboard.html", {
        "title": "Dashboard",
        "total_employees": total_employees,
        "employees_this_month": employees_this_month,
        "total_payment": total_payment,
        "paid_count": paid_count,
        "pending_count": pending_count,
        "paid_percent": paid_percent,
        "pending_percent": pending_percent,
        "current_month_name": current_month_name,

        "monthly_payment": monthly_payment,

        "total_absent": total_absent,
        "total_present": total_present,
        "total_leave": total_leave,
        "total_ot_hours": total_ot_hours,

        "recent_activities": recent_activities,
    })




@login_required
@permission_required("main.view_employee", raise_exception=True)
def employee_test(request):
    return render(request, "employees/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_department", raise_exception=True)
def department_test(request):
    return render(request, "departments/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_position", raise_exception=True)
def position_test(request):
    return render(request, "positions/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_attendance", raise_exception=True)
def attendance_test(request):
    return render(request, "attendance/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_payroll", raise_exception=True)
def payroll_test(request):
    return render(request, "payroll/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_payment", raise_exception=True)
def payments_test(request):
    return render(request, "payments/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_payslip", raise_exception=True)
def payslips_test(request):
    return render(request, "payslips/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_report", raise_exception=True)
def reports_test(request):
    return render(request, "reports/test.html", {
        "title": "test"
    })


@login_required
@permission_required("main.view_setting", raise_exception=True)
def settings_test(request):
    return render(request, "settings/test.html", {
        "title": "test"
    })




#test
#this require login and permission to view the test page
@login_required
@permission_required("main.view_employee", raise_exception=True)
def test(request):
    employees = Employee.objects.all()

    return render(request, "test.html", {
        "employees": employees
    })


