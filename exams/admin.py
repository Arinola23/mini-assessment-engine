from django.contrib import admin
from .models import Exam, Question, Submission

# Register your models here.
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class ExamAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

admin.site.register(Exam, ExamAdmin)
admin.site.register(Submission)
