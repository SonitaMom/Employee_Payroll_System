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


    path("attendance/test/", views.attendance_test, name="attendance_test"),


    path("payroll/test/", views.payroll_test, name="payroll_test"),


    path("payments/test/", views.payments_test, name="payments_test"),


    path("payslips/test/", views.payslips_test, name="payslips_test"),


    path("reports/test/", views.reports_test, name="reports_test"),


    path("settings/test/", views.settings_test, name="settings_test"),


    #test
    path("test/", views.test, name="test"),
]
