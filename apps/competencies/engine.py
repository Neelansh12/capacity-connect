"""
Transparent Rule-Based Recommendation Engine for Trainer Discovery
SIH26075 - Ministry of Earth Sciences (MoES) Capacity Building

Scoring Formula (Normalized to 0 - 100%):
1. Competency Proficiency Match:
   - Expert: 4.0 pts
   - Advanced: 3.0 pts
   - Intermediate: 2.0 pts
   - Beginner: 1.0 pt
   Summed across all query-matching competencies.
   Max possible proficiency points = 4.0 * len(query_competencies)

2. Experience Factor:
   - Added experience bonus = min(avg_years_in_competencies * 0.15, 2.0)

3. Track Record / Courses Conducted Factor:
   - Added courses bonus = min(published_courses_count * 0.3, 1.5)

4. Final Score:
   Raw Score = Proficiency_Pts + Experience_Bonus + Courses_Bonus
   Max Theoretical Score = (4.0 * N) + 2.0 + 1.5
   Match Percentage = min(round((Raw Score / Max Theoretical Score) * 100, 1), 100.0)
"""

from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from .models import Competency, TrainerCompetency, Proficiency

User = get_user_model()

def recommend_trainers_for_competencies(competency_ids, min_experience=0, min_proficiency=None):
    """
    Given a list of competency IDs, computes match scores and returns
    ranked list of recommended trainers with transparent scoring metrics.
    """
    if not competency_ids:
        return []

    target_competencies = list(Competency.objects.filter(id__in=competency_ids))
    num_targets = len(target_competencies)
    if num_targets == 0:
        return []

    # Find trainers mapped to any of the target competencies
    trainer_mappings = TrainerCompetency.objects.filter(
        competency_id__in=competency_ids,
        trainer__is_active=True,
        trainer__approval_status='APPROVED'
    ).select_related('trainer', 'trainer__department', 'trainer__designation', 'competency', 'trainer__trainer_profile')

    if min_experience > 0:
        trainer_mappings = trainer_mappings.filter(experience_years__gte=min_experience)

    # Group by trainer
    trainer_data = {}
    for mapping in trainer_mappings:
        trainer = mapping.trainer
        if trainer.id not in trainer_data:
            trainer_data[trainer.id] = {
                'trainer': trainer,
                'mappings': [],
                'matching_competencies': [],
                'total_prof_pts': 0.0,
                'total_exp': 0,
            }

        prof_pts = mapping.get_proficiency_weight()
        trainer_data[trainer.id]['mappings'].append(mapping)
        trainer_data[trainer.id]['matching_competencies'].append({
            'name': mapping.competency.name,
            'proficiency': mapping.get_proficiency_level_display(),
            'experience_years': mapping.experience_years,
            'points': prof_pts,
        })
        trainer_data[trainer.id]['total_prof_pts'] += prof_pts
        trainer_data[trainer.id]['total_exp'] += mapping.experience_years

    # Calculate final scores
    recommendations = []
    max_theoretical = (4.0 * num_targets) + 2.0 + 1.5

    for tid, info in trainer_data.items():
        trainer = info['trainer']
        match_count = len(info['mappings'])
        avg_exp = info['total_exp'] / match_count if match_count else 0
        exp_bonus = min(avg_exp * 0.15, 2.0)

        # Courses conducted
        courses_count = getattr(trainer, 'authored_courses', None)
        conducted_count = courses_count.filter(status='PUBLISHED').count() if courses_count else 0
        course_bonus = min(conducted_count * 0.3, 1.5)

        raw_score = info['total_prof_pts'] + exp_bonus + course_bonus
        match_percentage = min(round((raw_score / max_theoretical) * 100.0, 1), 100.0)

        # Extract avatar & profile details
        profile = getattr(trainer, 'trainer_profile', None)

        recommendations.append({
            'trainer': trainer,
            'profile': profile,
            'match_percentage': match_percentage,
            'raw_score': round(raw_score, 2),
            'matching_count': match_count,
            'total_targets': num_targets,
            'matching_competencies': info['matching_competencies'],
            'courses_conducted': conducted_count,
            'avg_experience_years': round(avg_exp, 1),
            'scoring_breakdown': {
                'proficiency_pts': round(info['total_prof_pts'], 1),
                'experience_bonus': round(exp_bonus, 2),
                'course_bonus': round(course_bonus, 2),
            }
        })

    # Sort by match percentage descending
    recommendations.sort(key=lambda x: (x['match_percentage'], x['matching_count']), reverse=True)
    return recommendations

