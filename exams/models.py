from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Exam Model
class Exam(models.Model):
    title = models.CharField(max_length=255)
    duration = models.IntegerField()  # minutes
    course = models.CharField(max_length=100)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

# Question Model
class Question(models.Model):
    QUESTION_TYPES = (
        ("mcq", "Multiple Choice"),
        ("text", "Text Answer"),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    expected_answer = models.JSONField()
    # expected_answer = models.TextField()


    def __str__(self):
        return f"{self.question_text[:50]}..."
        
# Submission Model - score included
class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    answers = models.JSONField(default=dict)  
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["exam"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.exam}"