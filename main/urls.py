from django.urls import path
from django.views.generic import TemplateView
from . import views

# urlpatterns = [
#     path("", TemplateView.as_view(template_name="login.html"), name='login'),
#     path("dashboard/", TemplateView.as_view(template_name="dashboard.html"), name='dashboard'),
# ]

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    #test
    path("test/", views.test, name="test"),
]
