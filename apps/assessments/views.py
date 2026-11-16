from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Assessment, Question, AnswerOption, AssessmentAttempt, SubmittedAnswer
from .forms import AssessmentForm, QuestionForm
from apps.courses.models import Course, Enrollment
from apps.accounts.decorators import approval_required, trainer_required

@login_required
@approval_required
def assessment_detail_view(request, course_slug):
    """Assessment instructions and history screen."""
    course = get_object_or_404(Course, slug=course_slug)
    assessment = get_object_or_404(Assessment, course=course)

    # Check enrollment
    enrollment = Enrollment.objects.filter(employee=request.user, course=course).first()
    if not enrollment and not (request.user == course.trainer or request.user.is_admin_role()):
        messages.error(request, "You must be enrolled in the course to attempt this assessment.")
        return redirect('courses:detail', slug=course.slug)

    # Check previous attempts
    attempts = AssessmentAttempt.objects.filter(assessment=assessment, employee=request.user).order_by('-attempt_number')
    attempts_count = attempts.count()
    can_attempt = attempts_count < assessment.max_attempts and assessment.is_active_now()
    best_attempt = attempts.filter(passed=True).first()

    return render(request, 'assessments/detail.html', {
        'course': course,
        'assessment': assessment,
        'attempts': attempts,
        'attempts_count': attempts_count,
        'can_attempt': can_attempt,
        'best_attempt': best_attempt,
        'enrollment': enrollment,
    })

@login_required
@approval_required
def assessment_take_view(request, course_slug):
    """Active test taking screen with server-side validation and timer."""
    course = get_object_or_404(Course, slug=course_slug)
    assessment = get_object_or_404(Assessment, course=course)

    # Verify course enrollment before allowing an assessment attempt.
    enrollment = Enrollment.objects.filter(
        employee=request.user,
        course=course
    ).first()

    if not enrollment and not (
        request.user == course.trainer or request.user.is_admin_role()
    ):
        messages.error(
            request,
            "You must be enrolled in the course to attempt this assessment."
        )
        return redirect('courses:detail', slug=course.slug)

    # Check eligibility
    attempts_count = AssessmentAttempt.objects.filter(assessment=assessment, employee=request.user).count()
    if attempts_count >= assessment.max_attempts:
        messages.error(request, "You have reached the maximum allowed attempts for this assessment.")
        return redirect('assessments:detail', course_slug=course.slug)

    if not assessment.is_active_now():
        messages.error(request, "This assessment is not currently active.")
        return redirect('assessments:detail', course_slug=course.slug)

    questions = assessment.questions.prefetch_related('options').order_by('order')
    if not questions.exists():
        messages.warning(request, "No questions have been configured for this assessment yet.")
        return redirect('assessments:detail', course_slug=course.slug)

    if request.method == 'POST':
        # Server-side score evaluation
        total_marks = 0.0
        score_obtained = 0.0

        attempt_num = attempts_count + 1
        attempt = AssessmentAttempt.objects.create(
            assessment=assessment,
            employee=request.user,
            attempt_number=attempt_num,
            total_marks=0.0,
            score_obtained=0.0,
            percentage_obtained=0.0,
            passed=False
        )

        for q in questions:
            total_marks += q.marks
            selected_option_id = request.POST.get(f'question_{q.id}')
            selected_option = None
            is_correct = False

            if selected_option_id:
                try:
                    selected_option = q.options.get(id=selected_option_id)
                    if selected_option.is_correct:
                        is_correct = True
                        score_obtained += q.marks
                except AnswerOption.DoesNotExist:
                    pass

            SubmittedAnswer.objects.create(
                attempt=attempt,
                question=q,
                selected_option=selected_option,
                is_correct=is_correct
            )

        percentage = round((score_obtained / total_marks) * 100.0, 1) if total_marks > 0 else 0.0
        passed = percentage >= assessment.passing_percentage

        attempt.total_marks = total_marks
        attempt.score_obtained = score_obtained
        attempt.percentage_obtained = percentage
        attempt.passed = passed
        attempt.save()

        # Update enrollment completion status if passed
        enrollment = Enrollment.objects.filter(employee=request.user, course=course).first()
        if enrollment and passed:
            enrollment.is_completed = True
            enrollment.completed_at = timezone.now()
            enrollment.save()

            # Attempt automatic certificate issuance
            try:
                from apps.certificates.services import issue_certificate_if_eligible
                cert = issue_certificate_if_eligible(enrollment)
                if cert:
                    messages.success(request, "Congratulations! You passed the assessment and your Certificate of Completion has been issued!")
            except Exception as e:
                pass

        if passed:
            messages.success(request, f"Assessment completed! You scored {percentage}%. You PASSED!")
        else:
            messages.warning(request, f"Assessment completed. You scored {percentage}%. Passing criteria: {assessment.passing_percentage}%.")

        return redirect('assessments:result', attempt_id=attempt.id)

    return render(request, 'assessments/take.html', {
        'course': course,
        'assessment': assessment,
        'questions': questions,
        'attempt_number': attempts_count + 1,
    })

@login_required
@approval_required
def attempt_result_view(request, attempt_id):
    """View result and breakdown of an assessment attempt."""
    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related('assessment', 'assessment__course', 'employee'), 
        id=attempt_id
    )

    # Authorization check
    is_owner = (attempt.employee == request.user)
    is_course_trainer = (attempt.assessment.course.trainer == request.user)
    is_admin = request.user.is_admin_role()

    if not (is_owner or is_course_trainer or is_admin):
        raise PermissionDenied("You do not have permission to view these assessment results.")

    answers = attempt.submitted_answers.select_related('question', 'selected_option').all()

    return render(request, 'assessments/result.html', {
        'attempt': attempt,
        'answers': answers,
        'course': attempt.assessment.course,
    })

# Trainer Assessment Management
@trainer_required
def trainer_assessment_manage_view(request, course_id):
    """Create or configure assessment for a course."""
    course = get_object_or_404(Course, id=course_id)
    if course.trainer != request.user and not request.user.is_admin_role():
        raise PermissionDenied("You cannot configure assessments for courses you do not own.")

    assessment = getattr(course, 'assessment', None)

    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course = course
            assessment.save()
            messages.success(request, "Assessment settings updated successfully.")
            return redirect('assessments:manage_questions', assessment_id=assessment.id)
    else:
        form = AssessmentForm(instance=assessment)

    return render(request, 'trainer/assessment_form.html', {
        'form': form,
        'course': course,
        'assessment': assessment,
    })

@trainer_required
def trainer_questions_manage_view(request, assessment_id):
    """Add and view questions for an assessment."""
    assessment = get_object_or_404(Assessment.objects.select_related('course'), id=assessment_id)
    if assessment.course.trainer != request.user and not request.user.is_admin_role():
        raise PermissionDenied("Unauthorized access.")

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_question':
            form = QuestionForm(request.POST)
            if form.is_valid():
                q = form.save(commit=False)
                q.assessment = assessment
                q.save()

                # Save 4 options
                correct_idx = int(form.cleaned_data['correct_option'])
                options = [
                    (form.cleaned_data['option_1'], 1),
                    (form.cleaned_data['option_2'], 2),
                    (form.cleaned_data['option_3'], 3),
                    (form.cleaned_data['option_4'], 4),
                ]
                for text, idx in options:
                    AnswerOption.objects.create(
                        question=q,
                        option_text=text,
                        is_correct=(idx == correct_idx),
                        order=idx
                    )

                messages.success(request, f"Question added successfully.")
                return redirect('assessments:manage_questions', assessment_id=assessment.id)
        elif action == 'delete_question':
            q_id = request.POST.get('question_id')
            q = get_object_or_404(Question, id=q_id, assessment=assessment)
            q.delete()
            messages.info(request, "Question deleted.")
            return redirect('assessments:manage_questions', assessment_id=assessment.id)
    else:
        next_order = assessment.questions.count() + 1
        form = QuestionForm(initial={'order': next_order, 'marks': 1})

    questions = assessment.questions.prefetch_related('options').order_by('order')
    return render(request, 'trainer/questions_manage.html', {
        'assessment': assessment,
        'course': assessment.course,
        'questions': questions,
        'form': form,
    })

