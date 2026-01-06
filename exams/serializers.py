from rest_framework import serializers
from .models import Exam, Question, Submission

#register
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

#Admin access
class AdminQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question_text", "question_type", "expected_answer"]
        # extra_kwargs = {
        #     "expected_answer": {"required": False},
        #     }

class AdminExamSerializer(serializers.ModelSerializer):
     class Meta:
        model = Exam
        fields = ["id", "title", "duration", "course", "metadata", "questions"]

     questions = AdminQuestionSerializer(many=True)
   
     def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        exam = Exam.objects.create(**validated_data)

        for question_data in questions_data:
            Question.objects.create(exam=exam, **question_data)
        return exam

# 
class AdminUpdateExamSerializer(serializers.ModelSerializer):
    questions = AdminQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Exam
        fields = "__all__"

        def update(self, instance, validated_data):
            # Update only exam info
            instance.title = validated_data.get("title", instance.title)
            instance.duration = validated_data.get("duration", instance.duration)
            instance.course = validated_data.get("course", instance.course)
            instance.save()
            return instance


# Students limited access
class StudentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question_text", "question_type"] 


class StudentExamSerializer(serializers.ModelSerializer):
    questions = StudentQuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "duration", "course", "questions"]


#admin can see all students submission
class AdminSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.username", read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    exam_course = serializers.CharField(source="exam.course", read_only=True)

    class Meta:
        model = Submission
        # fields = "__all__"
        fields = [
            "id", #submission id
            "student", #student id
            "student_name",
            "exam",
            "exam_title",
            "exam_course",
            "answers",
            "score",
            "created_at"
        ]
        read_only_fields = ["student", "score"]

# a student can only see his/her submission.
class StudentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.username", read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    exam_course = serializers.CharField(source="exam.course", read_only=True)

    class Meta:
        model = Submission
        # fields = "__all__"
        fields = [
            "student_name",
            "exam_title",
            "exam_course",
            "score",
            "created_at"
        ]
        read_only_fields = ["score"]

