from django.urls import path
from .auth_views import RegisterView, LoginView
from .views import (
    ExamListView,
    SubmitExamView,
    AdminSubmissionView,
    ExamDetailView, 
    StudentSubmissionsView,
    CreateExamView,
    UpdateExamView,
    DeleteExamView,
    UpdateQuestionView,
    DeleteQuestionView,
)



urlpatterns = [
     path("auth/register/", RegisterView.as_view()), #post and token generation for each student.
    path("auth/login/", LoginView.as_view()), #post

        #Admin access, token generated from admin panel
    path("exams/create/", CreateExamView.as_view()), #post
    path("exams/<int:exam_id>/update/", UpdateExamView.as_view()),
    path("exams/<int:exam_id>/delete/", DeleteExamView.as_view()),
    path("questions/<int:question_id>/update/", UpdateQuestionView.as_view()),
    path("questions/<int:question_id>/delete/", DeleteQuestionView.as_view()),
    path("exams/", ExamListView.as_view()), #getAllExams & questions with expected answers by admin
    path("submissions/grade/Admin/", AdminSubmissionView.as_view()), #get

        #student access
    path("exams/<int:exam_id>/", ExamDetailView.as_view()), #get one exam and questions by students without answers
    path("exams/<int:exam_id>/submit/", SubmitExamView.as_view()), #post/submit answers
    path("submissions/grade/student", StudentSubmissionsView.as_view()), #get


]
