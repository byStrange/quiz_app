from django.urls import path
from . import views

app_name = "settings"

urlpatterns = [
    path("", views.index, name="index"),
    path("exams/", views.exams, name="exams"),
    path("users/", views.users, name="users"),
]
