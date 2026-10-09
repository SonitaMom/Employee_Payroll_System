from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),


    path("employees/test/", views.employee_test, name="employee_test"),



    path("departments/test/", views.department_test, name="department_test"),


    path("positions/test/", views.position_test, name="position_test"),


    path("attendance/record/", views.attendance_record, name="attendance_record"),

 

    path("payroll/", views.payroll, name="payroll"),
    path("payroll/new-payroll", views.new_payroll, name="new_payroll"),
    path("payroll/update/<int:payroll_id>/", views.update_payroll, name="update_payroll"),


    path("payments/test/", views.payments_test, name="payments_test"),


    path("payslips/test/", views.payslips_test, name="payslips_test"),


    path("reports/", views.reports, name="reports"),


    path("settings/test/", views.settings_test, name="settings_test"),


    #test
    path("test/", views.test, name="test"),
]
