from django.contrib.auth.models import User
from django.db import models
import uuid


class BasicUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city_and_school = models.CharField(max_length=255)
    faculty = models.CharField(max_length=100, default="_")
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE, blank=True, null=True)
    more_details = models.TextField()
    certificate = models.FileField(upload_to="certificates", blank=True, null=True)

    def __str__(self):
        return self.user.first_name
    

class QuestionType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Option(models.Model):
    text = models.CharField(max_length=100)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    is_true = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Question(models.Model):
    image = models.ImageField(upload_to="media/question-images", blank=True, null=True)
    text = models.TextField()
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)

    def add_option(self, text, is_correct=False):
        option = Option.objects.create(text=text, question=self, is_true=is_correct)
        return option

    def __str__(self):
        return self.text


class Exam(models.Model):
    name = models.CharField(max_length=100)
    subject1_questions = models.ManyToManyField(Question, related_name="subject1_exams")
    subject2_questions = models.ManyToManyField(Question, related_name="subject2_exams")

    def __str__(self):
        return self.name


class QuestionGroup(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.name


class Results(models.Model):
    user = models.ForeignKey(BasicUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.user.user.username} - {self.exam.name}"
