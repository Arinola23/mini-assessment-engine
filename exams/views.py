from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from .grading import grade_submission

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse

from .models import Exam, Submission, Question
from .serializers import (
    AdminExamSerializer,
    AdminUpdateExamSerializer,
    AdminSubmissionSerializer,
    StudentExamSerializer,
    StudentSubmissionSerializer,
    AdminQuestionSerializer
)

#Create Exams
@extend_schema_view(
    post=extend_schema(
        description="Admin-only: Create an exam with questions",
        request=AdminExamSerializer,
        responses={
            201: OpenApiResponse(
                description="Exam created successfully",
                examples=[
                    OpenApiExample(
                        name="Success",
                        value={"message": "Exam created", "exam_id": 1},
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples=[
                    OpenApiExample(
                        name="ValidationError",
                        value={"title": ["This field is required."]},
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            )
        },        examples=[
            OpenApiExample(
                name="Create Math Exam Example",
                summary="An example of creating an exam with questions",
                value={
                    "title": "Math Test",
                    "duration": 60,
                    "course": "Algebra",
                    "questions": [
                        {
                            "question_text": "What is 2+2?",
                            "question_type": "text",
                            "expected_answer": "4"
                        }
                    ]
                },
                request_only=True,  # request body
                response_only=False
            )
        ]
    )
)

class CreateExamView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = AdminExamSerializer(data=request.data)
        if serializer.is_valid():
            exam = serializer.save()
            return Response({"message": "Exam created", "exam_id": exam.id}, status=201)
        return Response(serializer.errors, status=400)


# Update Exam with id
@extend_schema_view(
    put=extend_schema(
        description="Admin-only: Update an exam's title, duration, or course. Questions can be omitted if unchanged.",
        request=AdminUpdateExamSerializer,
        responses={
            200: OpenApiResponse(
                description="Exam updated successfully",
                examples=[
                    OpenApiExample(
                        name="Success",
                        value={
                            "message": "Exam updated successfully",
                            "exam": {
                                "id": 5,
                                "title": "Math Test",
                                "duration": 60,
                                "course": "Algebra",
                                "metadata": None,
                                "questions": []  # If questions unchanged
                            }
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples=[
                    OpenApiExample(
                        name="ValidationError",
                        value={"title": ["This field may not be blank."]},
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        name="Forbidden",
                        value={"detail": "You do not have permission to perform this action."},
                        response_only=True
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Exam not found",
                examples=[
                    OpenApiExample(
                        name="NotFound",
                        value={"error": "Exam not found"},
                        response_only=True
                    )
                ]
            ),
        },
        examples=[
            OpenApiExample(
                name="Update Math Exam Example",
                summary="An example of updating an exam without changing questions",
                value={
                    "title": "Math Test",
                    "duration": 60,
                    "course": "Algebra"
                },
                request_only=True
            )
        ]
    )
)
class UpdateExamView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def put(self, request, exam_id):
        exam = Exam.objects.filter(id=exam_id).first()
        if not exam:
            return Response({"error": "Exam not found"}, status=404)

        serializer = AdminUpdateExamSerializer(exam, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Exam updated successfully"})
        return Response(serializer.errors, status=400)


# Delete Exam
@extend_schema(
    description="Delete an exam and all its questions (admin only).",
    responses={
        200: OpenApiResponse(
            description="Exam successfully deleted",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"message": "Exam deleted successfully"},
                    response_only=True
                )
            ]
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    name="Unauthorized",
                    value={"detail": "Authentication credentials were not provided."},
                    response_only=True
                )
            ]
        ),
        404: OpenApiResponse(
            description="Not Found",
            examples=[
                OpenApiExample(
                    name="ExamNotFound",
                    value={"error": "Exam not found"},
                    response_only=True
                )
            ]
        )
    },
)
class DeleteExamView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def delete(self, request, exam_id):
        exam = Exam.objects.filter(id=exam_id).first()
        if not exam:
            return Response({"error": "Exam not found"}, status=404)
        exam.delete()
        return Response({"message": "Exam deleted successfully"}, status=200)


# Update Question
@extend_schema_view(
    put=extend_schema(
        description="Admin-only: Update a single question by question_id.",
        request=AdminQuestionSerializer,
        responses={
            200: OpenApiResponse(
                description="Question updated successfully",
                examples=[
                    OpenApiExample(
                        name="Success",
                        value={
                            "message": "Question updated successfully",
                            "question": {
                                "id": 5,
                                "question_text": "What is 2+2+2?",
                                "question_type": "text",
                                "expected_answer": "6",
                                "exam": 3
                            }
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples=[
                    OpenApiExample(
                        name="ValidationError",
                        value={"question_text": ["This field may not be blank."]},
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        name="Forbidden",
                        value={"detail": "You do not have permission to perform this action."},
                        response_only=True
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Question not found",
                examples=[
                    OpenApiExample(
                        name="NotFound",
                        value={"error": "Question not found"},
                        response_only=True
                    )
                ]
            ),
        },
        examples=[
            OpenApiExample(
                name="Update Question Example",
                summary="Example of updating a question's text and answer",
                value={
                    "question_text": "What is 2+2+2?",
                    "question_type": "text",
                    "expected_answer": "6"
                },
                request_only=True
            )
        ]
    )
)
class UpdateQuestionView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def put(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if not question:
            return Response({"error": "Question not found"}, status=404)

        serializer = AdminQuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Question updated successfully"})
        return Response(serializer.errors, status=400)


# Delete Question
@extend_schema(
    description="Delete questions (admin only).",
    responses={
        200: OpenApiResponse(
            description="Question successfully deleted",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"message": "Question deleted successfully"},
                    response_only=True
                )
            ]
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    name="Unauthorized",
                    value={"detail": "Authentication credentials were not provided."},
                    response_only=True
                )
            ]
        ),
        404: OpenApiResponse(
            description="Not Found",
            examples=[
                OpenApiExample(
                    name="questionNotFound",
                    value={"error": "Question not found"},
                    response_only=True
                )
            ]
        )
    },
)
class DeleteQuestionView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def delete(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if not question:
            return Response({"error": "Question not found"}, status=404)
        question.delete()
        return Response({"message": "Question deleted successfully"}, status=200)


# ADMIN GET ALL EXAMS
@extend_schema_view(
    get=extend_schema(
        description="Admin-only: Retrieve a list of all exams, each including its nested questions.",
        responses={
            200: OpenApiResponse(
                description="List of exams with nested questions",
                examples=[
                    OpenApiExample(
                        name="Exams List Example",
                        summary="An example response showing exams with questions",
                        value=[
                            {
                                "id": 3,
                                "title": "Introduction to Python",
                                "duration": 60,
                                "course": "CSC101",
                                "metadata": None,
                                "questions": [
                                    {
                                        "id": 5,
                                        "question_text": "What is the correct file extension for Python files?",
                                        "question_type": "mcq",
                                        "expected_answer": ".py"
                                    },
                                    {
                                        "id": 6,
                                        "question_text": "Which keyword is used to define a function in Python?",
                                        "question_type": "mcq",
                                        "expected_answer": "def"
                                    }
                                ]
                            }
                        ],
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        name="Forbidden",
                        value={"detail": "You do not have permission to perform this action."},
                        response_only=True
                    )
                ]
            )
        }
    )
)

class ExamListView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        exams = Exam.objects.all().prefetch_related("questions")
        serializer = AdminExamSerializer(exams, many=True)
        return Response(serializer.data)


# STUDENT GET A SINGLE EXAM
@extend_schema_view(
    get=extend_schema(
        description="Retrieve exam details for students. Includes all questions but excludes correct answers if configured.",
        responses={
            200: OpenApiResponse(
                description="Exam details for a student",
                examples=[
                    OpenApiExample(
                        name="Student Exam Example",
                        summary="Example of a student fetching exam details with questions",
                        value={
                            "id": 2,
                            "title": "Introduction to Python",
                            "duration": 60,
                            "course": "CSC101",
                            "metadata": None,
                            "questions": [
                                {
                                    "id": 5,
                                    "question_text": "What is the correct file extension for Python files?",
                                    "question_type": "mcq",
                                    # Optional: hide expected_answer for students
                                    "expected_answer": None
                                },
                                {
                                    "id": 6,
                                    "question_text": "Which keyword is used to define a function in Python?",
                                    "question_type": "mcq",
                                    "expected_answer": None
                                }
                            ]
                        },
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Exam not found",
                examples=[
                    OpenApiExample(
                        name="NotFound",
                        value={"error": "Exam not found"},
                        response_only=True
                    )
                ]
            )
        }
    )
)

class ExamDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        serializer = StudentExamSerializer(exam)
        return Response(serializer.data)


# STUDENT SUBMIT EXAM
@extend_schema_view(
    post=extend_schema(
        description="Submit answers for an exam. Key is question ID, value is answer.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "answers": {"type": "object"}
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="Submission successful",
                examples=[
                    OpenApiExample(
                        name="SubmissionSuccess",
                        value={
                            "message": "Submission successful",
                            "score": 33.33
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples=[
                    OpenApiExample(
                        name="ValidationError",
                        value={"answers": ["This field is required."]},
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Exam not found",
                examples=[
                    OpenApiExample(
                        name="ExamNotFound",
                        value={"error": "Exam not found"},
                        response_only=True
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name="Submit Exam Example",
                summary="Example of submitting answers",
                value={
                    "answers": {
                        "5": "Python",
                        "6": "def",
                        "7": "A variable stores data."
                    }
                },
                request_only=True
            )
        ]
    )
)

class SubmitExamView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)

        # Prevent duplicate submissions
        existing = Submission.objects.filter(student=request.user, exam=exam).first()
        if existing:
            return Response(
                {"message": "You have already submitted this exam.", "score": existing.score},
                status=400
            )

        submission = Submission.objects.create(
            student=request.user,
            exam=exam,
            answers=request.data.get("answers")
        )

        score = grade_submission(exam, submission)
        submission.score = score
        submission.save()

        return Response({"message": "Submitted successfully", "score": score})
        

# ADMIN GET ALL SUBMISSIONS
@extend_schema_view(
    get=extend_schema(
        description="Admin-only: Retrieve all students' exam submissions.",
        responses={
            200: OpenApiResponse(
                description="List of submissions",
                examples=[
                    OpenApiExample(
                        name="SubmissionsExample",
                        summary="Example response showing all student submissions",
                        value=[
                            {
                                "id": 5,
                                "student": 2,
                                "student_name": "student15",
                                "exam": 3,
                                "exam_title": "Introduction to Python",
                                "exam_course": "CSC101",
                                "answers": {
                                    "5": ".py",
                                    "6": "def",
                                    "7": "A variable is a name used to holding stored data."
                                },
                                "score": 33.33,
                                "created_at": "2026-01-04T15:42:44.509533Z"
                            },
                            {
                                "id": 8,
                                "student": 5,
                                "student_name": "Arinola",
                                "exam": 3,
                                "exam_title": "Introduction to Python",
                                "exam_course": "CSC101",
                                "answers": {
                                    "5": ".py",
                                    "6": "def",
                                    "7": "A variable is a named storage used to hold data."
                                },
                                "score": 33.33,
                                "created_at": "2026-01-05T10:50:03.127844Z"
                            }
                        ],
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        name="Forbidden",
                        value={"detail": "You do not have permission to perform this action."},
                        response_only=True
                    )
                ]
            )
        }
    )
)

class AdminSubmissionView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        submissions = Submission.objects.all()
        serializer = AdminSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


# STUDENT VIEW OWN SUBMISSIONS
@extend_schema_view(
    get=extend_schema(
        description="Retrieve your submission history. Only returns submissions for the authenticated student.",
        responses={
            200: OpenApiResponse(
                description="List of student submissions",
                examples=[
                    OpenApiExample(
                        name="MySubmissions",
                        summary="Example of a student's submission history",
                        value=[
                            {
                                "id": 5,
                                "student": 2,
                                "student_name": "student15",
                                "exam": 3,
                                "exam_title": "Introduction to Python",
                                "exam_course": "CSC101",
                                "answers": {
                                    "5": ".py",
                                    "6": "def",
                                    "7": "A variable is a name used to holding stored data."
                                },
                                "score": 33.33,
                                "created_at": "2026-01-04T15:42:44.509533Z"
                            },
                            {
                                "id": 8,
                                "student": 5,
                                "student_name": "Arinola",
                                "exam": 3,
                                "exam_title": "Introduction to Python",
                                "exam_course": "CSC101",
                                "answers": {
                                    "5": ".py",
                                    "6": "def",
                                    "7": "A variable is a named storage used to hold data."
                                },
                                "score": 33.33,
                                "created_at": "2026-01-05T10:50:03.127844Z"
                            }
                        ],
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True
                    )
                ]
            )
        }
    )
)

class StudentSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        submissions = Submission.objects.filter(student=request.user)
        serializer = StudentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)



