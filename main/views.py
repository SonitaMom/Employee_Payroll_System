from django.shortcuts import render

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from .models import Employee
#anna task
from .models import Employee, Department, Position, Payroll
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
def dashboard(request):
    return render(request, "dashboard.html", {
        "title": "Dashboard"
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




















#Anna tasks
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.contrib import messages
from .models import Employee, Department, Position, Payroll

# 1. EMPLOYEES VIEW (Handles Listing & Modal Creation)
def employee_list(request):
    if request.method == "POST":
        Employee.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            department_id=request.POST.get('department'),
            position_id=request.POST.get('position'),
            hire_date=request.POST.get('hire_date'),
            sex=request.POST.get('sex'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            status="Active"
        )
        messages.success(request, "Employee profile successfully saved to database!")
        return redirect('employee_list')
        
    context = {
        'employees': Employee.objects.select_related('department', 'position').all(),
        'departments': Department.objects.all(),
        'positions': Position.objects.all(),
    }
    return render(request, 'employees/test.html', context)

# 2. DEPARTMENTS VIEW (Handles Grid Display & Quick Save)
def department_list(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        Department.objects.create(name=name, description=description)
        messages.success(request, f"Department '{name}' added successfully.")
        return redirect('department_list')
        
    departments = Department.objects.annotate(emp_count=Count('employees')).all()
    return render(request, 'departments/test.html', {'departments': departments})

# 3. POSITIONS VIEW (Handles Tiers, Salaries & OT calculation mapping)
def position_list(request):
    if request.method == "POST":
        name = request.POST.get('name')
        basic_salary = request.POST.get('basic_salary')
        ot_rate = request.POST.get('ot_rate')
        description = request.POST.get('description')
        Position.objects.create(name=name, basic_salary=basic_salary, ot_rate=ot_rate, description=description)
        messages.success(request, f"Job tier position '{name}' successfully updated.")
        return redirect('position_list')
        
    positions = Position.objects.all()
    return render(request, 'positions/test.html', {'positions': positions})

# 4. PAYSLIPS VIEW (Renders the itemized payout blocks)
def payslip_list(request):
    payrolls = Payroll.objects.select_related('employee', 'employee__position', 'employee__department').prefetch_related('items').all()
    return render(request, 'payslips/test.html', {'payrolls': payrolls})

# 5. REPORTS VIEW (Compiles active database aggregates for your dashboard graphics)
def report_dashboard(request):
    context = {
        'total_employees': Employee.objects.count(),
        'total_departments': Department.objects.count(),
        'total_positions': Position.objects.count(),
        'total_payroll_exp': Payroll.objects.aggregate(Sum('net_salary'))['net_salary__sum'] or 0.00
    }
    return render(request, 'reports/test.html', context)
