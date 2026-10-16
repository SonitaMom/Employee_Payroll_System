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

    path("attendance/", views.attendance, name="attendance"),
    path("attendance/record/", views.attendance_record, name="attendance_record"),
    path("attendance/add/", views.attendance_add, name="attendance_add"),
    path("attendance/<int:pk>/edit/", views.attendance_edit, name="attendance_edit"),

    path("payroll/", views.payroll, name="payroll"),
    path("payroll/new-payroll", views.new_payroll, name="new_payroll"),
    path("payroll/update/<int:payroll_id>/", views.update_payroll, name="update_payroll"),
    path("payroll/delete/<int:payroll_id>/", views.delete_payroll, name="delete_payroll"),
    path("payroll/api/calc/", views.api_payroll_calc, name="api_payroll_calc"),


    path("payments/payment/", views.payments_test, name="payments"),
    path("payments/<int:pk>/complete/", views.payment_complete, name="payment_complete"),
    path("payments/paymentDetail/", views.payment_details, name="payment_details"),
    path("payments/payment/details/", views.payment_details, name="payment_details"),

    path("payslips/test/", views.payslips_test, name="payslips_test"),


    path("reports/", views.reports, name="reports"),


    path("settings/", views.settings, name="settings"),


    #test
    path("test/", views.test, name="test"),
]
