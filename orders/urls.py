from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup_view, name="signup"),
    path("payment", views.payment_view, name="payment"),
    path("pay", views.pay, name="pay"),
    path("error", views.error_view, name="error"),
]
 