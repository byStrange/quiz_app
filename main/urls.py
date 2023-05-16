from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("test/", views.test, name="test")
]
