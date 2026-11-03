from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Competency, TrainerCompetency, EmployeeCompetency
from .forms import CompetencyForm, TrainerCompetencyForm, EmployeeCompetencyForm
from .engine import recommend_trainers_for_competencies
from apps.accounts.decorators import approval_required, trainer_required, admin_required

def competency_library_view(request):
    """Browse organizational competency library."""
    query = request.GET.get('q', '').strip()
    domain = request.GET.get('domain', '')

    competencies = Competency.objects.annotate(
        trainer_count=Count('trainer_mappings', distinct=True),
        course_count=Count('course_outcomes', distinct=True)
    ).order_by('name')

    if query:
        competencies = competencies.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if domain:
        competencies = competencies.filter(domain=domain)

    domains = Competency.Domain.choices

    return render(request, 'competencies/library.html', {
        'competencies': competencies,
        'domains': domains,
        'selected_domain': domain,
        'search_query': query,
    })

def trainer_discovery_view(request):
    """
    Explainable Trainer Discovery & Recommendation Interface.
    Allows searching by multiple competencies, domain, and experience.
    """
    selected_comp_ids = request.GET.getlist('competencies')
    min_exp_str = request.GET.get('min_experience', '0')
    domain_filter = request.GET.get('domain', '')

    try:
        min_experience = int(min_exp_str)
    except ValueError:
        min_experience = 0

    all_competencies = Competency.objects.all().order_by('domain', 'name')
    if domain_filter:
        all_competencies = all_competencies.filter(domain=domain_filter)

    selected_ids_ints = []
    for cid in selected_comp_ids:
        try:
            selected_ids_ints.append(int(cid))
        except ValueError:
            pass

    recommendations = []
    if selected_ids_ints:
        recommendations = recommend_trainers_for_competencies(
            selected_ids_ints, 
            min_experience=min_experience
        )

    return render(request, 'competencies/trainer_discovery.html', {
        'all_competencies': all_competencies,
        'selected_comp_ids': selected_ids_ints,
        'min_experience': min_experience,
        'domain_filter': domain_filter,
        'recommendations': recommendations,
        'domains': Competency.Domain.choices,
    })

@trainer_required
def trainer_skills_view(request):
    """Manage competencies mapped to the logged-in trainer."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = TrainerCompetencyForm(request.POST)
            if form.is_valid():
                mapping = form.save(commit=False)
                mapping.trainer = request.user
                mapping.save()
                messages.success(request, f"Competency '{mapping.competency.name}' added to your profile.")
                return redirect('competencies:trainer_skills')
        elif action == 'delete':
            mapping_id = request.POST.get('mapping_id')
            mapping = get_object_or_404(TrainerCompetency, id=mapping_id, trainer=request.user)
            mapping.delete()
            messages.info(request, "Competency removed from your profile.")
            return redirect('competencies:trainer_skills')
    else:
        form = TrainerCompetencyForm()

    my_skills = TrainerCompetency.objects.filter(trainer=request.user).select_related('competency')
    return render(request, 'trainer/skills_manage.html', {
        'form': form,
        'my_skills': my_skills,
    })

@login_required
@approval_required
def employee_skills_view(request):
    """Manage skills & target competencies for employees."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = EmployeeCompetencyForm(request.POST)
            if form.is_valid():
                mapping = form.save(commit=False)
                mapping.employee = request.user
                mapping.save()
                messages.success(request, f"Skill '{mapping.competency.name}' recorded.")
                return redirect('competencies:employee_skills')
        elif action == 'delete':
            mapping_id = request.POST.get('mapping_id')
            mapping = get_object_or_404(EmployeeCompetency, id=mapping_id, employee=request.user)
            mapping.delete()
            messages.info(request, "Skill removed from your profile.")
            return redirect('competencies:employee_skills')
    else:
        form = EmployeeCompetencyForm()

    current_skills = EmployeeCompetency.objects.filter(employee=request.user, is_target_skill=False).select_related('competency')
    target_skills = EmployeeCompetency.objects.filter(employee=request.user, is_target_skill=True).select_related('competency')

    return render(request, 'employee/skills_manage.html', {
        'form': form,
        'current_skills': current_skills,
        'target_skills': target_skills,
    })

