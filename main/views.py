from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json
import random

from main.models import BasicUser, Exam, QuestionGroup, Option, Question, Results

#from .functions import create_certificate


# Create your views here.


@csrf_exempt
def register(request):
    if request.method == "POST":
        # data = json.load(request)
        data = json.load(request).get("data")
        name = data["full_name"]
        username = name.replace(" ", "")
        metrka_series = data["metrka_series"].replace(" ", "").trim()
        if BasicUser.objects.filter(metrka_series=metrka_series).exists():
            return JsonResponse(
                {
                    "status": False,
                    "error_code": "user has already passed exam",
                    "student": {
                        "uuid": BasicUser.objects.get(metrka_series=metrka_series).id
                    },
                }
            )

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
            user=user,
            faculty=faculty,
            city_and_school=city_and_school,
            metrka_series=metrka_series,
        )
        basic_user.save()
        login(request, user)
        return JsonResponse(
            {
                "status": True,
                "student": {
                    "username": user.username,
                    "name": user.first_name,
                    "faculty": faculty,
                    "city_and_school": city_and_school,
                    "uuid": basic_user.id,
                },
            }
        )
    else:
        return JsonResponse({"status": "Only POST request allowed"})


@csrf_exempt
def login_view(request, token):
    basic_user = BasicUser.objects.get(id=token)
    if basic_user.results_set.exists():
        login(request, basic_user.user)
        return render(request, "main/index.html", {"attempts_end": True})
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

    exam = Exam(name=f"Exam ({user.id})")
    print(exam, "new EXAMMMM")
    try:
        question_group_1 = random.sample(
            list(question_group_1_store.questions.all()), 10
        )
        print("GOOTTTTTTTT", question_group_2_store)
    except:
        q1_list = list(question_group_1_store.question.all())
        question_group_1 = random.sample(q1_list, len(q1_list))
        print("EXWEVECEECETIPONM", question_group_1_store)
    try:
        question_group_2 = random.sample(
            list(question_group_2_store.questions.all()), 10
        )
        print("GOOOOOOOOOOOOOOOOOT22222", question_group_2_store)
    except:
        q2_list = list(question_group_2_store.questions.all())
        question_group_2 = random.sample(q2_list, len(q2_list))
        print("EXECPPCPCPEPPPC 2", question_group_2_store)
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
        attempts_end = False
        if basic_user.results_set.exists():
            attempts_end = True

        options = Option.objects.all()
        return render(
            request,
            "main/index.html",
            {
                "basic_user": basic_user,
                "options": options,
                "attempts_end": attempts_end,
            },
        )


def test(request, slug):
    question_group = QuestionGroup.objects.get(name=slug)
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

            # Print the question and its options
            question = Question.objects.get(id=question_id)
            print(f"Question: {question.text}")
            print("Options:")
            for option in question.option_set.all():
                print(f"- {option.text}")

            # Print the correct option and the option selected by the user
            correct_option_id = question_option_mapping.get(question_id)
            correct_option = Option.objects.get(id=correct_option_id)
            selected_option = Option.objects.get(id=selected_option_id)
            print(f"Correct Option: {correct_option.text}")
            print(f"Selected Option: {selected_option.text}")

            # Check if the selected option is correct and update the score
            if (
                question_id in question_option_mapping
                and selected_option_id == question_option_mapping[question_id]
            ):
                score += 1
        if basic_user.results_set.exists():
            return JsonResponse({"succeed": False})
        else:
            result = Results(user=basic_user, exam=basic_user.exam, score=score)
            result.save()

        # Print the final score
        print(f"Score: {score}")

        # Return the response
        return JsonResponse({"succeed": True})

    # Handle GET request or other cases
    return JsonResponse({"status": "Only POST request allowed"})


@csrf_exempt
def exam_results(request):
    print(request.user)
    basic_user = BasicUser.objects.get(user=request.user)
    results = Results.objects.filter(user=basic_user).order_by("-id")
    result = results.first()
    result_questions_count = (
        result.exam.subject1_questions.count() + result.exam.subject2_questions.count()
    )
    passed = False
    percentage = (result.score / result_questions_count) * 100
    city_and_school = basic_user.city_and_school.split(
        ","
    )  # "Andijon, 23-umuiny o'rta talim"
    filled_data_wrong = False

    if percentage >= 60:
        passed = True
        try:
            city = city_and_school[0]
            school = city_and_school[1]
            student = {
                "name": basic_user.user.first_name,
                "uuid": basic_user.id,
                "city": city,
                "school": school,
                "id": str(basic_user.user.id),
            }
        except:
            filled_data_wrong = True

        if not filled_data_wrong:
            create_certificate(student)

    incorrect = result_questions_count - result.score
    attempts_end = False
    if basic_user.results_set.exists():
        attempts_end = True
    return render(
        request,
        "main/result.html",
        {
            "result": result,
            "question_count": result_questions_count,
            "incorrect": incorrect,
            "passed": passed,
            "attempts_end": attempts_end,
            "filled_data_wrong": filled_data_wrong,
        },
    )


def certificate_pdf_view(request, certificate_id):
    # Construct the file path based on the certificate_id and the folder location
    try:
        file_path = os.path.join("media", "certificate", f"{certificate_id}.pdf")

        # Open the PDF file in binary mode
        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/pdf")

        # Set the filename in the Content-Disposition header
        response["Content-Disposition"] = f'attachment; filename="{certificate_id}.pdf"'
    except:
        response = HttpResponse("there is no certificate for this user")
    return response
