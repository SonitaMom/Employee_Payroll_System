from django.contrib import admin
from . import models

admin.site.register(models.Department)
admin.site.register(models.Position)
admin.site.register(models.Employee)
admin.site.register(models.Attendance)
admin.site.register(models.Payroll)
admin.site.register(models.PayrollItem)
admin.site.register(models.Payment)
