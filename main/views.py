from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json
import random

from main.models import BasicUser, Exam, QuestionGroup, Option, Question, Results

from .functions import create_certificate


# Create your views here.


@csrf_exempt
def register(request):
    if request.method == "POST":
        # data = json.load(request)
        data = json.load(request).get("data")
        name = data["full_name"]
        username = name.replace(" ", "")

        if not User.objects.filter(username=username).exists():
            user = User(username=username, first_name=name)
            user.save()
        else:
            user = User(
                username=f"{username}{random.randint(0, 9999)}", first_name=name
            )
            user.save()

        city_and_school = data["city_and_school"]
        faculty = data["faculty"]
        basic_user = BasicUser(
            user=user, faculty=faculty, city_and_school=city_and_school
        )
        basic_user.save()
        login(request, user)
        return JsonResponse(
            {
                "student": {
                    "username": user.username,
                    "name": user.first_name,
                    "faculty": faculty,
                    "city_and_school": city_and_school,
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
    if faculty == "IG":
        question_group_1_store = QuestionGroup.objects.get(name="History")
        question_group_2_store = QuestionGroup.objects.get(name="Geography")
    if faculty == "TF":
        question_group_1_store = QuestionGroup.objects.get(name="Chemistry")
        question_group_2_store = QuestionGroup.objects.get(name="Biology")

    if not basic_user.exam:
        exam = Exam(name=f"Exam ({user.id})")
        print(len(list(question_group_2_store.questions.all())))
        print(question_group_2_store)
        try:
            question_group_1 = random.sample(
                list(question_group_1_store.questions.all()), 10
            )
        except:
            q1_list = list(question_group_1_store.question.all())
            question_group_1_store = random.sample(q1_list, len(q1_list))
        try:
            question_group_2 = random.sample(
                list(question_group_2_store.questions.all()), 10
            )
        except:
            q2_list = list(question_group_2_store.questions.all())
            question_group_2 = random.sample(q2_list, len(q2_list))
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
        options = Option.objects.all()
        return render(
            request, "main/index.html", {"basic_user": basic_user, "options": options}
        )


def test(request):
    question_group = QuestionGroup.objects.get(name="Math")
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
        return JsonResponse({"succeed": True})

    # Handle GET request or other cases
    return JsonResponse({"status": "Only POST request allowed"})


@csrf_exempt
def exam_results(request):
    basic_user = BasicUser.objects.get(user=request.user)
    results = Results.objects.filter().order_by("-id")
    result = results.first()
    result_questions_count = (
        result.exam.subject1_questions.count() + result.exam.subject2_questions.count()
    )
    passed = False
    percentage = (result.score / result_questions_count) * 100
    city_and_school = basic_user.city_and_school.split(
        ","
    )  # "Andijon, 23-umuiny o'rta talim"
    city = city_and_school[0]
    school = city_and_school[1]

    student = {
        "name": basic_user.user.first_name,
        "uuid": basic_user.id,
        "city": city,
        "school": school,
        "id": str(basic_user.user.id),
    }
    print(percentage)
    if percentage >= 60:
        passed = True
        create_certificate(student)

    incorrect = result_questions_count - result.score
    return render(
        request,
        "main/result.html",
        {
            "result": result,
            "question_count": result_questions_count,
            "incorrect": incorrect,
            "passed": passed,
        },
    )


def certificate_pdf_view(request, certificate_id):
    # Construct the file path based on the certificate_id and the folder location
    file_path = os.path.join("media", "certificate", f"{certificate_id}.pdf")

    # Open the PDF file in binary mode
    with open(file_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")

    return response
