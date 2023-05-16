from django.contrib.auth.models import User
from django.db import models
import uuid


class BasicUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    more_details = models.TextField()


class QuestionType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Option(models.Model):
    text = models.CharField(max_length=100)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Question(models.Model):
    text = models.TextField()
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def add_option(self, text, is_correct=False):
        option = Option.objects.create(
            text=text, question=self, is_correct=is_correct)
        return option


class Exam(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question)

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
