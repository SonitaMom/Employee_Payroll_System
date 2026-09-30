from django.core.validators import MinValueValidator
from django.db import models


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    position_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    basic_salary = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    ot_rate = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    class SexChoices(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    class StatusChoices(models.TextChoices):
        ACTIVE = "Active", "Active"
        INACTIVE = "Inactive", "Inactive"

    employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    sex = models.CharField(
        max_length=6, choices=SexChoices.choices, blank=True, null=True
    )
    image = models.ImageField(upload_to="employees/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    position = models.ForeignKey(
        Position, on_delete=models.PROTECT, related_name="employees"
    )
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="employees"
    )

    hire_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"


class Attendance(models.Model):
    class StatusChoices(models.TextChoices):
        PRESENT = "Present", "Present"
        ABSENT = "Absent", "Absent"
        LEAVE = "Leave", "Leave"

    attendance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendances"
    )

    date = models.DateField()
    check_in = models.TimeField(blank=True, null=True)
    check_out = models.TimeField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PRESENT,
    )
    ot_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    note = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"], name="unique_employee_attendance_date"
            )
        ]

    def __str__(self):
        return f"{self.employee_id} - {self.date} ({self.status})"


class Payroll(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = "Draft", "Draft"
        APPROVED = "Approved", "Approved"
        PAID = "Paid", "Paid"

    payroll_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="payrolls"
    )

    pay_period = models.DateField()

    # Salary snapshot at the time payroll is created
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)

    # Money calculated from overtime
    ot_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Final salary after bonuses, allowances, deductions, and tax
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "pay_period"], name="unique_employee_pay_period"
            )
        ]

    def __str__(self):
        return f"Payroll #{self.payroll_id} - {self.employee_id} ({self.pay_period})"


class PayrollItem(models.Model):
    class ItemTypeChoices(models.TextChoices):
        BONUS = "Bonus", "Bonus"
        ALLOWANCE = "Allowance", "Allowance"
        DEDUCTION = "Deduction", "Deduction"
        TAX = "Tax", "Tax"

    payroll_item_id = models.AutoField(primary_key=True)
    payroll = models.ForeignKey(
        Payroll, on_delete=models.CASCADE, related_name="items"
    )

    type = models.CharField(max_length=20, choices=ItemTypeChoices.choices)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.type} - {self.name}: {self.amount}"


class Payment(models.Model):
    class MethodChoices(models.TextChoices):
        CASH = "Cash", "Cash"
        BANK_TRANSFER = "Bank Transfer", "Bank Transfer"

    class StatusChoices(models.TextChoices):
        PENDING = "Pending", "Pending"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"

    payment_id = models.AutoField(primary_key=True)
    # 1-to-1 mapping as specified by `Ref: Payroll.payroll_id - Payment.payroll_id`
    payroll = models.OneToOneField(
        Payroll, on_delete=models.PROTECT, related_name="payment"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(
        max_length=30, choices=MethodChoices.choices, blank=True, null=True
    )
    reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment #{self.payment_id} - Payroll #{self.payroll_id} ({self.status})"