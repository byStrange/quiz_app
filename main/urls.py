from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("api/register", views.register, name="register"),
    path("api/login/<str:token>/", views.login_view, name="login"),
    path("exam/", views.exam_view, name="exam"),
    path("exam-check/", views.exam_check, name="exam_check"),
    path("exam-results/", views.exam_results, name="exam_results"),

    # test
    path("test/", views.test, name="test")
]
