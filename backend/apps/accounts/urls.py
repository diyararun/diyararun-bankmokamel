from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.auth_page, name="auth"),
    path("otp/request/", views.request_otp, name="otp_request"),
    path("otp/verify/", views.verify_otp, name="otp_verify"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("orders/", views.order_list_view, name="orders"),
    path("orders/<str:tracking_code>/", views.order_detail_view, name="order_detail"),
]