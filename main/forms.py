from django import forms
from .models import Attendance


class AttendanceForm(forms.ModelForm):          # used by Add
    class Meta:
        model  = Attendance
        fields = ["employee", "check_in", "check_out", "status"]


class AttendanceEditForm(forms.ModelForm):      # used by Edit (employee is locked)
    class Meta:
        model  = Attendance
        fields = ["check_in", "check_out", "status"]