from django import forms
from .models import Attendance, Payroll, PayrollItem
from django.forms import inlineformset_factory


class AttendanceForm(forms.ModelForm):
    class Meta:
        model  = Attendance
        fields = ["employee", "check_in", "check_out", "status"]


class AttendanceEditForm(forms.ModelForm):
    class Meta:
        model  = Attendance
        fields = ["check_in", "check_out", "status"]


class PayrollForm(forms.ModelForm):
    pay_period = forms.DateField(
        input_formats=["%Y-%m", "%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "month",
                "id": "id_pay_period",
            },
            format="%Y-%m",
        ),
    )

    class Meta:
        model = Payroll
        fields = ["employee", "pay_period"]

        widgets = {
            "employee": forms.Select(
                attrs={"class": "form-select", "id": "id_employee"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If updating existing payroll, employee cannot be changed
        if self.instance and self.instance.pk:
            self.fields["employee"].disabled = True
            # Format instance date to YYYY-MM for HTML5 month input
            if self.instance.pay_period:
                self.initial["pay_period"] = self.instance.pay_period.strftime("%Y-%m")

    def clean_pay_period(self):
        # Normalize the selected date to the first day of its month
        pay_period = self.cleaned_data.get("pay_period")
        if pay_period:
            return pay_period.replace(day=1)
        return pay_period


class PayrollItemForm(forms.ModelForm):
    class Meta:
        model = PayrollItem
        fields = ["name", "type", "amount", "description"]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control item-name", "placeholder": "Item name"}
            ),
            "type": forms.Select(
                attrs={"class": "form-select item-type"}
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control item-amount",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control item-desc",
                    "placeholder": "Optional description",
                }
            ),
        }


PayrollItemFormSet = inlineformset_factory(
    Payroll,
    PayrollItem,
    form=PayrollItemForm,
    extra=0,
    can_delete=True,
)