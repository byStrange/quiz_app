from django.urls import path
from . import views

app_name = "settings"

urlpatterns = [
    path("", views.index, name="index"),
    path("exams/", views.exams, name="exams"),
    path("exams/<int:pk>/", views.exam_details, name="exam"),
    path("exams/add/", views.add_exam, name="add_exams"),
    path("question-groups/", views.question_groups, name="question_groups"),
    path("question-groups/<int:pk>/", views.question_group, name="question_group",),
    path("users/", views.users, name="users"),
    path("users/<str:pk>/", views.user, name="user")
]
