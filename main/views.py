from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from decimal import Decimal 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from .models import Employee, Department, Position, Payroll, Payment
from datetime import date
from calendar import monthrange
import calendar
from django.http import HttpResponse
from main.services.dashboard import get_recent_activities

from .forms import AttendanceForm, AttendanceEditForm, PayrollForm, PayrollItemFormSet
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.db import transaction
from .services.payroll import calculate_payroll


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











# no need
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


def employees_data():
    return list(Employee.objects.values(
        "employee_id", "first_name", "last_name", "department_id"
    ))


@login_required
@permission_required("main.view_attendance", raise_exception=True)
def attendance(request):
    today=timezone.localdate().isoformat()
    start = request.GET.get("start", today)
    end = request.GET.get("end", today)
    dept = request.GET.get("dept", "")
    status = request.GET.get("status", "")
    dept_id = int(dept) if dept.isdigit() else None

    qs = (Attendance.objects.select_related("employee__department")
          .filter(date__range=[start, end]))
    if dept:
        qs=qs.filter(employee__department_id=dept)
    if status:
        qs = qs.filter(status=status)
    qs = qs.order_by("-date", "-pk")

    page=Paginator(qs, 10).get_page(request.GET.get("page"))

    total = page.paginator.count
    offset = page.start_index()-1 if total else 0
    for i, a in enumerate(page):
        a.row_no =total-offset-i

    return render(request, "attendance/attendance.html", {
        "title": "Attendance",
        "page" : page,
        "departments" : Department.objects.all(),
        "dept_id" : dept_id,
        "statuses": Attendance.StatusChoices.choices,
        "start": start, "end":end, "dept":dept, "status":status,
        "employees": employees_data(),
    })



def _back(request):
    """Return to the page the user came from (keeps filters and page)."""
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect("attendance")

def attendance_add(request):
    form = AttendanceForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please choose a department and an employee.")
        return _back(request)

    obj = form.save(commit=False)
    posted_dept = request.POST.get("department")
    if posted_dept and str(obj.employee.department_id) != posted_dept:
        messages.error(request, "That employee is not in the selected department.")
    elif Attendance.objects.filter(employee=obj.employee,
                                   date=timezone.localdate()).exists():
        messages.error(request, "This employee already has a record today.")
    else:
        obj.save()
        messages.success(request, "Attendance added.")
    return _back(request)

def attendance_edit(request, pk):
    obj  = get_object_or_404(Attendance, pk=pk)
    form = AttendanceEditForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()       
        messages.success(request, "Attendance updated.")
    else:
        messages.error(request, "Could not save. Please check the times.")
    return _back(request)

@login_required
@permission_required("main.view_attendance", raise_exception=True)
def attendance_record(request):
    today = date.today()

    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))

    days_in_month = monthrange(year, month)[1]

    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)

    employees = Employee.objects.filter(
        hire_date__lte=month_end
    ).filter(
        Q(inactive_date__isnull=True) |
        Q(inactive_date__gte=month_start)
    ).order_by("employee_id")

    attendance = Attendance.objects.filter(
        date__year=year,
        date__month=month,
    )

    attendance_map = {
        (item.employee_id, item.date.day): item.status
        for item in attendance
    }

    status_short = {
        "Present": "P",
        "Absent": "A",
        "Leave": "L",
    }

    attendance_rows = []

    for employee in employees:
        days = []
        present = 0
        absent = 0
        leave = 0

        for day in range(1, days_in_month + 1):
            status = attendance_map.get(
                (employee.employee_id, day)
            )

            days.append(status_short.get(status, "-"))

            if status == "Present":
                present += 1
            elif status == "Absent":
                absent += 1
            elif status == "Leave":
                leave += 1

        attendance_rows.append({
            "employee": employee,
            "days": days,
            "present": present,
            "absent": absent,
            "leave": leave,
        })

    return render(request, "attendance/record.html", {
        "title": "Attendance Record",
        "attendance_rows": attendance_rows,
        "days_in_month": range(1, days_in_month + 1),
        "month": month,
        "year": year,
    })










@login_required
@permission_required("main.view_payroll", raise_exception=True)
def payroll(request):
    today = date.today()

    months = list(enumerate(calendar.month_name))[1:]
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))
    search = request.GET.get("search", "").strip()

    payrolls = Payroll.objects.select_related("employee").filter(
        pay_period__year=year,
        pay_period__month=month,
    )

    if search:
        payrolls = payrolls.filter(
            Q(employee__employee_id__icontains=search)
            | Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
        )

    payrolls = payrolls.order_by("employee__employee_id")

    return render(request, "payroll/payroll.html", {
        "title": "Payroll",
        "payrolls": payrolls,
        "months": months,
        "month": month,
        "year": year,
        "search": search,
    })





from django.http import JsonResponse
from decimal import Decimal


@login_required
@permission_required("main.add_payroll", raise_exception=True)
def new_payroll(request):
    today = date.today()

    if request.method == "POST":
        form = PayrollForm(request.POST)
        formset = PayrollItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            payroll = form.save(commit=False)

            # Check if user clicked "Approve" button
            is_approve = "approve" in request.POST
            payroll.status = Payroll.StatusChoices.APPROVED if is_approve else Payroll.StatusChoices.DRAFT

            # Collect the submitted payroll items
            items = [
                item_form.cleaned_data
                for item_form in formset.forms
                if item_form.cleaned_data
                and not item_form.cleaned_data.get("DELETE", False)
            ]

            # Calculate salary using trusted backend logic
            result = calculate_payroll(
                employee=payroll.employee,
                pay_period=payroll.pay_period,
                payroll_items=items,
            )

            payroll.basic_salary = result["basic_salary"]
            payroll.ot_amount = result["ot_amount"]
            payroll.net_salary = result["net_salary"]

            # Save payroll and its items together
            with transaction.atomic():
                payroll.save()
                formset.instance = payroll
                formset.save()

            if is_approve:
                messages.success(request, f"Payroll for {payroll.employee.full_name} created and approved.")
            else:
                messages.success(request, f"Payroll for {payroll.employee.full_name} saved as Draft.")
            return redirect("payroll")
        else:
            # Send validation errors as Django messages
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields and form.fields[field].label else field.replace("_", " ").title()
                    messages.error(request, f"{field_name}: {error}")
            for err_dict in formset.errors:
                for k, errors in err_dict.items():
                    for error in errors:
                        messages.error(request, f"Item {k}: {error}")

    else:
        # Default pay period to today (current month)
        initial_period = date(today.year, today.month, 1)
        form = PayrollForm(initial={"pay_period": initial_period})
        formset = PayrollItemFormSet()

    # Pre-serialize employee salary & OT rate data for client-side calculation
    employees_data = {
        str(emp.pk): {
            "name": emp.full_name,
            "basic_salary": float(emp.position.basic_salary),
            "ot_rate": float(emp.position.ot_rate),
        }
        for emp in Employee.objects.select_related("position").filter(status=Employee.StatusChoices.ACTIVE)
    }

    return render(
        request,
        "payroll/form.html",
        {
            "form": form,
            "formset": formset,
            "payroll": None,
            "employees_data": employees_data,
            "title": "New Payroll",
        },
    )


@login_required
@permission_required("main.change_payroll", raise_exception=True)
def update_payroll(request, payroll_id):
    payroll = get_object_or_404(Payroll.objects.select_related("employee__position"), payroll_id=payroll_id)

    if request.method == "POST":
        form = PayrollForm(request.POST, instance=payroll)
        formset = PayrollItemFormSet(request.POST, instance=payroll)

        if form.is_valid() and formset.is_valid():
            payroll = form.save(commit=False)

            is_approve = "approve" in request.POST
            if is_approve:
                payroll.status = Payroll.StatusChoices.APPROVED

            # Collect the submitted payroll items
            items = [
                item_form.cleaned_data
                for item_form in formset.forms
                if item_form.cleaned_data
                and not item_form.cleaned_data.get("DELETE", False)
            ]

            # Recalculate salary
            result = calculate_payroll(
                employee=payroll.employee,
                pay_period=payroll.pay_period,
                payroll_items=items,
            )

            payroll.basic_salary = result["basic_salary"]
            payroll.ot_amount = result["ot_amount"]
            payroll.net_salary = result["net_salary"]

            with transaction.atomic():
                payroll.save()
                formset.save()

            if is_approve:
                messages.success(request, f"Payroll for {payroll.employee.full_name} updated and approved.")
            else:
                messages.success(request, f"Payroll for {payroll.employee.full_name} updated successfully.")
            return redirect("payroll")
        else:
            # Send validation errors as Django messages
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields and form.fields[field].label else field.replace("_", " ").title()
                    messages.error(request, f"{field_name}: {error}")
            for err_dict in formset.errors:
                for k, errors in err_dict.items():
                    for error in errors:
                        messages.error(request, f"Item {k}: {error}")
    else:
        form = PayrollForm(instance=payroll)
        formset = PayrollItemFormSet(instance=payroll)

    employees_data = {
        str(emp.pk): {
            "name": emp.full_name,
            "basic_salary": float(emp.position.basic_salary),
            "ot_rate": float(emp.position.ot_rate),
        }
        for emp in Employee.objects.select_related("position").all()
    }

    return render(
        request,
        "payroll/form.html",
        {
            "form": form,
            "formset": formset,
            "payroll": payroll,
            "employees_data": employees_data,
            "title": "Update Payroll",
        },
    )


@login_required
@permission_required("main.delete_payroll", raise_exception=True)
def delete_payroll(request, payroll_id):
    if request.method == "POST":
        payroll = get_object_or_404(Payroll, payroll_id=payroll_id)
        emp_name = payroll.employee.full_name
        payroll.delete()
        messages.success(request, f"Payroll for {emp_name} has been deleted.")
    return redirect("payroll")


@login_required
@permission_required("main.view_payroll", raise_exception=True)
def api_payroll_calc(request):
    """AJAX helper to calculate OT hours, OT amount and basic salary for chosen employee & month."""
    emp_id = request.GET.get("employee_id")
    period_str = request.GET.get("pay_period")  # format: YYYY-MM

    if not emp_id or not period_str:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        parts = period_str.split("-")
        y, m = int(parts[0]), int(parts[1])
        period_date = date(y, m, 1)
        employee = Employee.objects.select_related("position").get(pk=emp_id)
        calc = calculate_payroll(employee=employee, pay_period=period_date, payroll_items=[])
        return JsonResponse({
            "basic_salary": float(calc["basic_salary"]),
            "ot_hours": float(calc["ot_hours"]),
            "ot_amount": float(calc["ot_amount"]),
            "net_salary": float(calc["net_salary"]),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)






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
def reports(request):
    return render(request, "reports.html", {
        "title": "Reports"
    })


@login_required
@permission_required("main.view_setting", raise_exception=True)
def settings(request):
    return render(request, "settings.html", {
        "title": "Settings"
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




















#anna tasks
# ==========================================
# 1. EMPLOYEES VIEW
# ==========================================
@login_required
def employee_list(request):
    if request.method == "POST":
        action = request.POST.get("action", "create")
        
        if action == "create":
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            department_id = request.POST.get("department")
            position_id = request.POST.get("position")
            hire_date = request.POST.get("hire_date")
            sex = request.POST.get("sex")
            phone = request.POST.get("phone", "").strip()
            email = request.POST.get("email", "").strip()
            address = request.POST.get("address", "").strip()
            status = request.POST.get("status", "Active")

            Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                department_id=department_id,
                position_id=position_id,
                hire_date=hire_date,
                sex=sex,
                phone=phone,
                email=email,
                address=address,
                status=status
            )
            messages.success(request, f"Employee {first_name} {last_name} created successfully!")
            return redirect("employee_list")

        elif action == "update":
            emp_id = request.POST.get("employee_id")
            emp = get_object_or_404(Employee, pk=emp_id)
            emp.first_name = request.POST.get("first_name", emp.first_name).strip()
            emp.last_name = request.POST.get("last_name", emp.last_name).strip()
            emp.department_id = request.POST.get("department", emp.department_id)
            emp.position_id = request.POST.get("position", emp.position_id)
            emp.hire_date = request.POST.get("hire_date") or emp.hire_date
            emp.sex = request.POST.get("sex", emp.sex)
            emp.phone = request.POST.get("phone", emp.phone)
            emp.email = request.POST.get("email", emp.email)
            emp.address = request.POST.get("address", emp.address)
            emp.status = request.POST.get("status", emp.status)
            emp.save()
            messages.success(request, f"Employee {emp.full_name} updated successfully!")
            return redirect("employee_list")

        elif action == "delete":
            emp_id = request.POST.get("employee_id")
            emp = get_object_or_404(Employee, pk=emp_id)
            emp_name = emp.full_name
            emp.delete()
            messages.success(request, f"Employee {emp_name} removed.")
            return redirect("employee_list")

    employees = Employee.objects.select_related("department", "position").all().order_by("-employee_id")
    departments = Department.objects.all().order_by("name")
    positions = Position.objects.all().order_by("name")

    context = {
        "title": "Employees",
        "employees": employees,
        "departments": departments,
        "positions": positions,
        "total_count": employees.count(),
        "active_count": employees.filter(status=Employee.StatusChoices.ACTIVE).count(),
        "inactive_count": employees.filter(status=Employee.StatusChoices.INACTIVE).count(),
    }
    return render(request, "employees/test.html", context)


# ==========================================
# 2. DEPARTMENTS VIEW
# ==========================================
@login_required
def department_list(request):
    if request.method == "POST":
        action = request.POST.get("action", "create")

        if action == "create":
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()
            if name:
                Department.objects.create(name=name, description=description)
                messages.success(request, f"Department '{name}' added successfully.")
            return redirect("department_list")

        elif action == "update":
            dept_id = request.POST.get("department_id")
            dept = get_object_or_404(Department, pk=dept_id)
            dept.name = request.POST.get("name", dept.name).strip()
            dept.description = request.POST.get("description", dept.description).strip()
            dept.save()
            messages.success(request, f"Department '{dept.name}' updated.")
            return redirect("department_list")

        elif action == "delete":
            dept_id = request.POST.get("department_id")
            dept = get_object_or_404(Department, pk=dept_id)
            if dept.employees.exists():
                messages.error(request, f"Cannot delete '{dept.name}' because it contains assigned employees.")
            else:
                dept.delete()
                messages.success(request, f"Department '{dept.name}' deleted.")
            return redirect("department_list")

    departments = Department.objects.annotate(employee_count=Count("employees")).order_by("name")
    context = {
        "title": "Departments",
        "departments": departments,
        "total_departments": departments.count(),
    }
    return render(request, "departments/test.html", context)


# ==========================================
# 3. POSITIONS VIEW
# ==========================================
@login_required
def position_list(request):
    if request.method == "POST":
        action = request.POST.get("action", "create")

        if action == "create":
            name = request.POST.get("name", "").strip()
            basic_salary = request.POST.get("basic_salary") or 0
            ot_rate = request.POST.get("ot_rate") or 0
            description = request.POST.get("description", "").strip()

            Position.objects.create(
                name=name,
                basic_salary=basic_salary,
                ot_rate=ot_rate,
                description=description
            )
            messages.success(request, f"Position '{name}' registered successfully.")
            return redirect("position_list")

        elif action == "update":
            pos_id = request.POST.get("position_id")
            pos = get_object_or_404(Position, pk=pos_id)
            pos.name = request.POST.get("name", pos.name).strip()
            pos.basic_salary = request.POST.get("basic_salary") or pos.basic_salary
            pos.ot_rate = request.POST.get("ot_rate") or pos.ot_rate
            pos.description = request.POST.get("description", pos.description).strip()
            pos.save()
            messages.success(request, f"Position '{pos.name}' updated successfully.")
            return redirect("position_list")

        elif action == "delete":
            pos_id = request.POST.get("position_id")
            pos = get_object_or_404(Position, pk=pos_id)
            if pos.employees.exists():
                messages.error(request, f"Cannot delete '{pos.name}' because active staff hold this position.")
            else:
                pos.delete()
                messages.success(request, f"Position '{pos.name}' deleted.")
            return redirect("position_list")

    positions = Position.objects.annotate(employee_count=Count("employees")).order_by("-basic_salary")
    context = {
        "title": "Positions",
        "positions": positions,
        "total_positions": positions.count(),
    }
    return render(request, "positions/test.html", context)


# ==========================================
# 4. PAYSLIPS VIEW
# ==========================================
@login_required
def payslip_list(request):
    payrolls = Payroll.objects.select_related(
        "employee", "employee__department", "employee__position", "payment"
    ).prefetch_related("items").all().order_by("-pay_period", "-payroll_id")

    paid_sum = payrolls.filter(status=Payroll.StatusChoices.PAID).aggregate(Sum("net_salary"))["net_salary__sum"] or 0
    pending_sum = payrolls.filter(status=Payroll.StatusChoices.APPROVED).aggregate(Sum("net_salary"))["net_salary__sum"] or 0

    context = {
        "title": "Payslips",
        "payrolls": payrolls,
        "total_count": payrolls.count(),
        "paid_sum": paid_sum,
        "pending_sum": pending_sum,
    }
    return render(request, "payslips/test.html", context)


# ==========================================
# 5. REPORTS DASHBOARD VIEW
# ==========================================
@login_required
def report_dashboard(request):
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status=Employee.StatusChoices.ACTIVE).count()
    inactive_employees = Employee.objects.filter(status=Employee.StatusChoices.INACTIVE).count()
    
    total_payroll_exp = Payroll.objects.aggregate(Sum("net_salary"))["net_salary__sum"] or 0.00
    paid_payroll_exp = Payroll.objects.filter(status=Payroll.StatusChoices.PAID).aggregate(Sum("net_salary"))["net_salary__sum"] or 0.00
    pending_payroll_exp = Payroll.objects.filter(status=Payroll.StatusChoices.APPROVED).aggregate(Sum("net_salary"))["net_salary__sum"] or 0.00

    # Department breakdown
    dept_distribution = list(
        Department.objects.annotate(count=Count("employees"))
        .values("name", "count")
    )
    
    # Monthly breakdown for the PayPro bar chart
    monthly_data = (
        Payroll.objects.values("pay_period")
        .annotate(total=Sum("net_salary"))
        .order_by("pay_period")[:6]
    )
    month_labels = [m["pay_period"].strftime("%b %Y") for m in monthly_data]
    month_amounts = [float(m["total"]) for m in monthly_data]

    context = {
        "title": "Payroll Report",
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
        "total_departments": Department.objects.count(),
        "total_positions": Position.objects.count(),
        "total_payroll_exp": total_payroll_exp,
        "paid_payroll_exp": paid_payroll_exp,
        "pending_payroll_exp": pending_payroll_exp,
        "dept_distribution": dept_distribution,
        "month_labels": month_labels,
        "month_amounts": month_amounts,
    }
    return render(request, "reports.html", context)


def teammate_placeholder(request):
    """Temporary placeholder for modules handled by teammates."""
    return HttpResponse(
        "<h3>This module is being developed by another teammate.</h3>"
        "<p><a href='/employees/'>Go to Employees</a> | "
        "<a href='/departments/'>Go to Departments</a> | "
        "<a href='/positions/'>Go to Positions</a> | "
        "<a href='/payslips/'>Go to Payslips</a> | "
        "<a href='/reports/'>Go to Reports</a></p>"
    )
def employee_create(request):
    if request.method == "POST":
        # Check if form.save() or Employee.objects.create(...) is called
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("employee_test")
        else:
            print("Form errors:", form.errors)  # This will print in terminal if validation fails
    else:
        form = EmployeeForm()
    return render(request, "employees/create.html", {"form": form})