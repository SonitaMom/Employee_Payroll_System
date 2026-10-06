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


@login_required
@permission_required("main.view_dashboard", raise_exception=True)
def dashboard(request):

    total_employees = Employee.objects.count()
    total_payment = Payment.objects.filter(status=Payment.StatusChoices.COMPLETED).aggregate(Sum('amount'))['amount__sum'] or 0
    paid_count = Payment.objects.filter(status=Payment.StatusChoices.COMPLETED).count()
    pending_count = Payment.objects.filter(status=Payment.StatusChoices.PENDING).count()

    monthly_payment = list(
    Payment.objects
    .filter(status="Completed")
    .annotate(month=TruncMonth("payment_date"))
    .values("month")
    .annotate(total=Sum("amount"))
    .order_by("month")
    )
    for item in monthly_payment:
        item["month"] = item["month"].strftime("%b %Y")
    
    total_absent = Attendance.objects.filter(date=timezone.now().date(), status=Attendance.StatusChoices.ABSENT).count()
    total_present = Attendance.objects.filter(date=timezone.now().date(), status=Attendance.StatusChoices.PRESENT).count()
    total_leave = Attendance.objects.filter(date=timezone.now().date(), status=Attendance.StatusChoices.LEAVE).count()
    total_ot_hours = Attendance.objects.filter(date=timezone.now().date()).aggregate(Sum('ot_hours'))['ot_hours__sum'] or 0



    return render(request, "dashboard.html", {
        "title": "Dashboard",
        "total_employees": total_employees,
        "total_payment": total_payment,
        "paid_count": paid_count,
        "pending_count": pending_count,

        "monthly_payment": monthly_payment,

        "total_absent": total_absent,
        "total_present": total_present,
        "total_leave": total_leave,
        "total_ot_hours": total_ot_hours,



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


