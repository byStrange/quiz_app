from django.contrib import admin

# Register your models here.

from main.models import (
    QuestionGroup,
    QuestionType,
    Question,
    BasicUser,
    Results,
    Option,
    Exam,
)

admin.site.register(QuestionType)
admin.site.register(QuestionGroup)
admin.site.register(Question)
admin.site.register(BasicUser)
admin.site.register(Results)
admin.site.register(Option)
admin.site.register(Exam)
