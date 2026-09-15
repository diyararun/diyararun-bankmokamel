from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("<slug:slug>/submit/", views.ReviewCreateView.as_view(), name="submit"),
]