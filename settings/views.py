from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.template.defaulttags import register
from django.views.decorators.csrf import csrf_exempt

import json

from main.models import Exam, BasicUser, Results, Question, QuestionGroup, QuestionType


@register.filter(name="split")
def split(value, key):
    value.split("key")
    return value.split(key)


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
    context = {"users": users}
    return render(request, "settings/users.html", context)


@csrf_exempt
def ban_user(request, uuid):
    user = BasicUser.objects.get(id=uuid)
    if request.method == "POST":
        user.is_banned = True
        user.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"is_banned": user.is_banned})


@staff_member_required
@csrf_exempt
def user(request, uuid):
    user = BasicUser.objects.get(id=uuid)
    try:
        result = Results.objects.get(user=user, exam=user.exam)
    except:
        result = {"score": "Topshirmagan"}
    context = {"user": user, "result": result}

    return render(request, "settings/user.html", context)


@staff_member_required
def add_exam(request):
    groupped_questions = QuestionGroup.objects.all()
    if request.method == "POST":
        data = request.POST
        name = data["exam_name"]
        exam = Exam.objects.create(
            name=name,
        )
        exam.save()
        return redirect("/settings/exams/")
    return render(
        request, "settings/add_exam.html", {"groupped_questions": groupped_questions}
    )


@staff_member_required
def exam_details(request, pk):
    exam = Exam.objects.get(pk=pk)
    return render(request, "settings/exam.html", {"exam": exam})


@staff_member_required
def question_groups(request):
    question_groups = QuestionGroup.objects.all()
    if request.method == "POST":
        data = request.POST
        name = data["group_name"]
        QuestionGroup.objects.create(name=name)
        return redirect("/settings/question-groups/")
    return render(
        request, "settings/questions.html", {"question_groups": question_groups}
    )


@staff_member_required
def question_group(request, pk):
    question_group = QuestionGroup.objects.get(pk=pk)
    if request.method == "POST":
        question_type = QuestionType.objects.get(name="multiple_choice")
        data = json.load(request)["data"]
        name = data["name"]
        question = Question(text=name, question_type=question_type)
        question.save()
        options = data["options"]
        for option in options:
            question.add_option(option["name"], is_correct=option["checked"])

        question_group.questions.add(question)
        question_group.save()
        return JsonResponse({"question": {"name": question.text, "id": question.id}})
    return render(
        request, "settings/question_group.html", {"question_group": question_group}
    )


@staff_member_required
def passed_users(request):
    passed_users = []
    results = Results.objects.all()
    for result in results:
        if result.score >= 12:
            passed_users.append(result)
    return render(request, "settings/passed_users.html", {"results": passed_users})
