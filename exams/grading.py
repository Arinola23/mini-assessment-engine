import json

def grade_submission(exam, submission):
    """
    Grades a student's submission for a given exam.
    Returns the score as a percentage (0-100).
    """

    total_questions = exam.questions.count()
    if total_questions == 0:
        return 0.0

    score = 0

    for question in exam.questions.all():
        # Fetch the student's answer for this question
        student_answer = submission.answers.get(str(question.id))

        # Skip if no answer provided
        if student_answer is None:
            continue

        #  text question
        if question.question_type == "text":
            expected = str(question.expected_answer).strip().lower()
            student_text = str(student_answer).strip().lower()

            # Split expected answer into keywords
            expected_keywords = expected.split()
            match_count = sum(1 for kw in expected_keywords if kw in student_text)

            # If 60% or more keywords match, count as correct
            if len(expected_keywords) == 0 or match_count / len(expected_keywords) >= 0.6:
                score += 1

        # multiple choice questions
        elif question.question_type == "mcq":
            try:
                # Load expected answer as list
                expected_list = json.loads(question.expected_answer) if isinstance(question.expected_answer, str) else question.expected_answer
                expected_list = sorted([str(x).strip() for x in expected_list])
            except:
                expected_list = []

            if isinstance(student_answer, list):
                student_list = sorted([str(x).strip() for x in student_answer])
            else:
                # skip, if student sends a wrong type,
                continue

            if student_list == expected_list:
                score += 1

    # Return percentage score rounded to 2 decimal places
    return round((score / total_questions) * 100, 2)
