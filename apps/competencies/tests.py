from django.test import TestCase
from apps.accounts.models import User, Department
from .models import Competency, TrainerCompetency, Proficiency
from .engine import recommend_trainers_for_competencies

class CompetenciesTestCase(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="NCMRWF", code="NCMRWF")
        
        self.trainer_expert = User.objects.create_user(
            username='trainer_exp',
            role=User.Role.TRAINER,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.trainer_beg = User.objects.create_user(
            username='trainer_beg',
            role=User.Role.TRAINER,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.comp1 = Competency.objects.create(name="Python Programming", domain=Competency.Domain.TECHNICAL)
        self.comp2 = Competency.objects.create(name="Numerical Weather Prediction", domain=Competency.Domain.SCIENTIFIC)

        # Map expert trainer: Expert in Python (10 yrs) and Expert in NWP (8 yrs)
        TrainerCompetency.objects.create(
            trainer=self.trainer_expert,
            competency=self.comp1,
            proficiency_level=Proficiency.EXPERT,
            experience_years=10
        )
        TrainerCompetency.objects.create(
            trainer=self.trainer_expert,
            competency=self.comp2,
            proficiency_level=Proficiency.EXPERT,
            experience_years=8
        )

        # Map beginner trainer: Beginner in Python (1 yr)
        TrainerCompetency.objects.create(
            trainer=self.trainer_beg,
            competency=self.comp1,
            proficiency_level=Proficiency.BEGINNER,
            experience_years=1
        )

    def test_explainable_recommendation_ranking(self):
        # Query for both competencies
        recommendations = recommend_trainers_for_competencies([self.comp1.id, self.comp2.id])
        
        self.assertGreaterEqual(len(recommendations), 2)
        top_rec = recommendations[0]
        second_rec = recommendations[1]

        # Expert trainer must rank higher than beginner
        self.assertEqual(top_rec['trainer'].id, self.trainer_expert.id)
        self.assertEqual(second_rec['trainer'].id, self.trainer_beg.id)
        self.assertGreater(top_rec['match_percentage'], second_rec['match_percentage'])
        self.assertEqual(top_rec['matching_count'], 2)
        self.assertEqual(second_rec['matching_count'], 1)

