from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import requests
import json
import random

from main.models import BasicUser, Exam, QuestionGroup, Option, Question, Results


# Create your views here.


@csrf_exempt
def register(request):
    if request.method == "POST":
        # data = json.load(request)
        data = json.load(request).get("data")
        name = data["full_name"]
        username = name.replace(" ", "")
        try:
            user = User(username=username, first_name=name)
        except:
            old_user = User.objects.get(username)
            user = User(f"{username}{old_user.id + 1}", first_name=name)

        user.save()
        city = data["city"]
        school = data["school"]
        faculty = data["faculty"]
        basic_user = BasicUser(user=user, city=city, school=school, faculty=faculty)
        basic_user.save()
        login(request, user)
        return JsonResponse(
            {
                "student": {
                    "name": user.first_name,
                    "faculty": faculty,
                    "city": city,
                    "school": school,
                    "uuid": basic_user.id,
                }
            }
        )
    else:
        return JsonResponse({"status": "Only POST request allowed"})


@csrf_exempt
def login_view(request, token):
    basic_user = BasicUser.objects.get(id=token)
    user = basic_user.user
    faculty = basic_user.faculty
    if faculty == "XF":
        question_group_1_store = QuestionGroup.objects.get(name="English")
        question_group_2_store = QuestionGroup.objects.get(name="MotherTongue")
    if faculty == "AFT":
        question_group_1_store = QuestionGroup.objects.get(name="Math")
        question_group_2_store = QuestionGroup.objects.get(name="Physics")
    if faculty == "AFI":
        question_group_1_store = QuestionGroup.objects.get(name="Math")
        question_group_2_store = QuestionGroup.objects.get(name="English")

    if not basic_user.exam:
        exam = Exam(name=f"Exam ({user.id})")
        question_group_1 = random.sample(
            list(question_group_1_store.questions.all()), 10
        )
        question_group_2 = random.sample(
            list(question_group_2_store.questions.all()), 10
        )
        exam.save()
        for question in question_group_1:
            exam.subject1_questions.add(question)
        exam.save()

        for question in question_group_2:
            exam.subject2_questions.add(question)

        exam.save()
        basic_user.exam = exam
        basic_user.save()

    login(request, user)
    return redirect("main:exam")


@csrf_exempt
def exam_view(request):
    if request.user.is_authenticated:
        basic_user = BasicUser.objects.get(user=request.user)
        questions = basic_user.exam.questions.all()
        options = Option.objects.filter(question__in=questions)
        return render(
            request, "main/index.html", {"basic_user": basic_user, "options": options}
        )


def test(request):
    question_group = QuestionGroup.objects.get(name="Ingliz tili")
    questions = question_group.questions.all()
    options = Option.objects.filter(question__in=questions)
    return render(
        request, "main/test.html", {"questions": questions, "options": options}
    )


@csrf_exempt
def exam_check(request):
    if request.method == "POST":
        # Retrieve the submitted form data
        selected_options = json.load(request)["data"]
        basic_user = BasicUser.objects.get(user=request.user)
        # Retrieve the questions and their corresponding correct options
        question_ids = [int(question_id) for question_id in selected_options.keys()]
        questions = Question.objects.filter(id__in=question_ids)
        question_option_mapping = {
            question.id: question.option_set.filter(is_true=True).first().id
            for question in questions
        }

        # Evaluate the user's answers and calculate the score
        score = 0
        for question_id, selected_option_id in selected_options.items():
            question_id = int(question_id)
            selected_option_id = int(selected_option_id)
            if (
                question_id in question_option_mapping
                and selected_option_id == question_option_mapping[question_id]
            ):
                score += 1

        result = Results(user=basic_user, exam=basic_user.exam, score=score)
        result.save()
        # Render the result page with the score
        return redirect("main:exam_results")

    # Handle GET request or other cases
    return JsonResponse({"status": "Only POST request allowed"})


@csrf_exempt
def exam_results(request):
    basic_user = BasicUser.objects.get(user=request.user)
    result = Results.objects.get(user=basic_user, exam=basic_user.exam)
    return render("main/result.html", {"result": result})
