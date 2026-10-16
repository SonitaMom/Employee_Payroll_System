from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from datetime import date
from calendar import monthrange
import calendar

from main.services.dashboard import get_recent_activities

from .forms import AttendanceForm, AttendanceEditForm, PayrollForm, PayrollItemFormSet
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.db import transaction
from .services.payroll import calculate_payroll
from django.shortcuts import render


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


                #Create the pending payment when approved
                if payroll.status == Payroll.StatusChoices.APPROVED:
                    Payment.objects.get_or_create(
                        payroll=payroll,
                        defaults={"amount": payroll.net_salary},
                    )

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

                #create the pending payment when approved
                if payroll.status == Payroll.StatusChoices.APPROVED:
                    Payment.objects.get_or_create(
                        payroll = payroll,
                        defaults={"amount":payroll.net_salary}
                    )

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

def _safe_next(request):
    """Redirect to the posted `next` URL if it is safe, else to the payments page."""
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect("payments_test")






@login_required
@permission_required("main.view_payment", raise_exception=True)
def payments_test(request):
    # if false back toc current month 
    today=date.today()
    try:
        year, month = map(int, request.GET.get("month", "").split("-"))
        selected=date(year, month,1)
    except ValueError:
        selected=today.replace(day=1)

    #12 months
    base=today.year *12 +today.month -1
    months =[date((base +i) // 12, (base +i) %12 +1,1) for i in range(-12,13)]

    month_qs=Payment.objects.select_related("payroll__employee").filter(payroll__pay_period__year=selected.year,
                payroll__pay_period__month=selected.month)

    def total(status=None):
        qs=month_qs.filter(status=status) if status else month_qs
        return qs.aggregate(t=Sum("amount"))["t"] or 0


    #Search _ status filter for table
    status = request.GET.get("status", "")
    q=request.GET.get("q", "").strip()
    qs = month_qs
    if status:
        qs=qs.filter(status__iexact=status)
    if q:
        qs = qs.filter(
            Q(payroll__employee__first_name__icontains=q)
            | Q(payroll__employee__last_name__icontains=q)
        )

    qs = qs.order_by("-payroll__pay_period", "-pk")
 
    page = Paginator(qs, 5).get_page(request.GET.get("page"))

    # Query string without "page", so Previous/Next keep month, status and search
    params = request.GET.copy()
    params.pop("page", None)

    # Approved payrolls of this month that have no payment yet (for "+ Add Payment")
    available_payrolls = Payroll.objects.select_related("employee").filter(
        pay_period__year=selected.year,
        pay_period__month=selected.month,
        status=Payroll.StatusChoices.APPROVED,
        payment__isnull=True,
    )

    methods = [c[0] for c in Payment.MethodChoices.choices]

    # page = Paginator(qs, 5).get_page(request.GET.get("page"))

    return render(request, "payments/payment.html", {
        "title": "Payment",
        "months": months,
        "selected": selected,
        "page": page,
        "status": status,
        "q": q,
        "keep": params.urlencode(),
        "total": total(),
        "pending": total(Payment.StatusChoices.PENDING),
        "paid": total(Payment.StatusChoices.COMPLETED),
        "available_payrolls": available_payrolls,
        "methods": methods,
    })


@login_required
@permission_required("main.view_payment", raise_exception=True)
def payment_details(request):
    """Separate page: pick an employee, see their employee / payroll / payment info."""
    today=date.today()
    try:
            year, month = map(int, request.GET.get("month", "").split("-"))
            selected=date(year, month,1)
    except ValueError:
            selected=today.replace(day=1)
    
        #12 months
    base=today.year *12 +today.month -1
    months =[date((base +i) // 12, (base +i) %12 +1,1) for i in range(-12,13)]
 
    payments = Payment.objects.select_related(
        "payroll__employee__department", "payroll__employee__position"
    ).filter(
        payroll__pay_period__year=selected.year,
        payroll__pay_period__month=selected.month,
    ).order_by("payroll__employee__first_name", "payroll__employee__last_name")
 
    payment = None
    pid = request.GET.get("payment", "")
    if pid.isdigit():
        payment = payments.filter(pk=pid).first()
 
    return render(request, "payments/paymentDetail.html", {
        "title": "Payment Details",
        "months": months,
        "selected": selected,
        "payments": payments,
        "payment": payment,
    })
 

@login_required
@permission_required("main.change_payment", raise_exception=True)
@require_POST
def payment_complete(request,pk):
    payment = get_object_or_404(
        Payment.objects.select_related("payroll__employee"),pk=pk
    )
    # back=request.POST.get("next") or "payments"
    method = request.POST.get("payment_method")
    if payment.status == Payment.StatusChoices.COMPLETED:
        messages.info(request, "This payment is already completed.")
        return _safe_next(request)

    if payment.payroll.status == Payroll.StatusChoices.DRAFT:
        messages.error(request, "Approve the payroll before completing the payment.")
        return _safe_next(request)


       
    if method in Payment.MethodChoices.values:
        payment.payment_method = method

    if not payment.payment_method:
        messages.error(request, "Choose a payment method first.")
        return _safe_next(request)

    with transaction.atomic():
        payment.status = Payment.StatusChoices.COMPLETED
        payment.payment_date = timezone.localdate()
        payment.save()

        payroll = payment.payroll
        payroll.status = Payroll.StatusChoices.PAID
        payroll.save()

    messages.success(request, f"Payment for {payroll.employee.full_name} completed.")
    return _safe_next(request)


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


