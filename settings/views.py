from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from main.models import Exam, BasicUser, Results, Question, QuestionGroup, QuestionType
from django.http import JsonResponse
import json


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


@staff_member_required
def user(request, pk):
    user = BasicUser.objects.get(id=pk)
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
