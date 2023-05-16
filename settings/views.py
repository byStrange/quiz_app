from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from main.models import Exam, BasicUser, Results


# Create your views here.
@staff_member_required
def index(request):
    return render(request, "settings/index.html")


@staff_member_required
def exams(request):
    exams = Exam.objects.all()
    context = {"exams": exams}
    return render(request, "settings/exams.html", context)

@staff_member_required
def users(request):
    users = BasicUser.objects.all()
    context = {"users", users}
    return render(request, "settings/users.html", context)