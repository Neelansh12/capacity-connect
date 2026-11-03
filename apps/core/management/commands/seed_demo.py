"""
Management Command: seed_demo
Populates database with realistic, end-to-end organizational capacity building data
Ministry of Earth Sciences (MoES) / Central Organizations (SIH26075)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, Department, Designation, EmployeeProfile, TrainerProfile
from apps.courses.models import Category, Course, CourseModule, LearningResource, Enrollment, ModuleProgress
from apps.competencies.models import Competency, TrainerCompetency, EmployeeCompetency, CourseCompetency, Proficiency
from apps.assessments.models import Assessment, Question, AnswerOption, AssessmentAttempt, SubmittedAnswer
from apps.certificates.models import Certificate
from apps.certificates.services import issue_certificate_if_eligible
from apps.communications.models import Announcement, Notification, CourseFeedback, TrainerResource

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive demo data for SIH 2026 presentation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing Capacity Connect Demo Dataset..."))

        # 1. DEPARTMENTS & DESIGNATIONS
        departments_info = [
            ("India Meteorological Department", "IMD", "National meteorological service and weather forecasting agency."),
            ("Indian National Centre for Ocean Information Services", "INCOIS", "Ocean observations, tsunami warnings, and advisory services."),
            ("National Centre for Medium Range Weather Forecasting", "NCMRWF", "Numerical weather prediction and supercomputing weather modeling."),
            ("Indian Institute of Tropical Meteorology", "IITM", "Advanced climate studies, monsoon dynamics, and atmospheric physics."),
            ("National Institute of Ocean Technology", "NIOT", "Ocean engineering, marine resources exploration, and deep-sea technology."),
        ]
        depts = {}
        for name, code, desc in departments_info:
            dept, _ = Department.objects.get_or_create(code=code, defaults={'name': name, 'description': desc})
            depts[code] = dept

        designations_info = [
            ("Scientist 'B'", "IMD", 1),
            ("Scientist 'C'", "IMD", 2),
            ("Scientist 'E' (Senior Meteorologist)", "IMD", 3),
            ("Ocean Data Analyst", "INCOIS", 1),
            ("Senior Oceanographer", "INCOIS", 3),
            ("HPC Systems Engineer", "NCMRWF", 2),
            ("Climate Modeler", "IITM", 2),
            ("Marine Instrumentation Engineer", "NIOT", 2),
        ]
        desigs = {}
        for title, dcode, lvl in designations_info:
            desig, _ = Designation.objects.get_or_create(
                title=title, 
                department=depts[dcode], 
                defaults={'level': lvl}
            )
            desigs[title] = desig

        # 2. ADMINISTRATOR
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Dr. Rajesh',
                'last_name': 'Sharma',
                'email': 'admin@moes.gov.in',
                'role': User.Role.ADMIN,
                'approval_status': User.ApprovalStatus.APPROVED,
                'is_staff': True,
                'is_superuser': True,
                'department': depts['IMD'],
                'designation': desigs["Scientist 'E' (Senior Meteorologist)"],
                'phone_number': '+91-11-24611001',
                'approved_at': timezone.now()
            }
        )
        if created:
            admin_user.set_password('Admin@12345')
            admin_user.save()
            EmployeeProfile.objects.create(
                user=admin_user, 
                employee_id='MOES-ADM-001', 
                experience_years=18,
                qualifications='Ph.D. in Atmospheric Physics, IIT Delhi'
            )
        self.stdout.write(self.style.SUCCESS("[OK] Administrator account verified: admin / Admin@12345"))

        # 3. TRAINERS
        trainers_data = [
            {
                'username': 'trainer_climate',
                'first_name': 'Dr. Sunita',
                'last_name': 'Rao',
                'email': 'sunita.rao@iitm.res.in',
                'department': depts['IITM'],
                'designation': desigs['Climate Modeler'],
                'qualifications': 'Ph.D. Earth & Planetary Sciences, Cambridge Postdoc',
                'experience': 14,
                'expertise': 'Coupled Climate Models, Monsoon Dynamics, Climate Change Projections',
                'bio': 'Principal Investigator on CMIP6 regional downscaling and tropical monsoon simulation.',
            },
            {
                'username': 'trainer_gis',
                'first_name': 'Dr. Alok',
                'last_name': 'Verma',
                'email': 'alok.verma@incois.gov.in',
                'department': depts['INCOIS'],
                'designation': desigs['Senior Oceanographer'],
                'qualifications': 'M.Tech Remote Sensing, Ph.D. Oceanography',
                'experience': 11,
                'expertise': 'Satellite Oceanography, GIS Spatial Analysis, Coastal Hazard Mapping',
                'bio': 'Lead scientist managing Indian Ocean operational satellite observational pipelines.',
            },
            {
                'username': 'trainer_ai',
                'first_name': 'Prof. Devendra',
                'last_name': 'Nair',
                'email': 'devendra.nair@ncmrwf.gov.in',
                'department': depts['NCMRWF'],
                'designation': desigs['HPC Systems Engineer'],
                'qualifications': 'Ph.D. Computer Science, M.S. Scientific Computing',
                'experience': 12,
                'expertise': 'Machine Learning in Weather Prediction, HPC Optimization, PyTorch',
                'bio': 'Specialist in deep neural networks for precipitation forecasting and supercomputing.',
            },
        ]
        trainers = {}
        for tinfo in trainers_data:
            t_user, created = User.objects.get_or_create(
                username=tinfo['username'],
                defaults={
                    'first_name': tinfo['first_name'],
                    'last_name': tinfo['last_name'],
                    'email': tinfo['email'],
                    'role': User.Role.TRAINER,
                    'approval_status': User.ApprovalStatus.APPROVED,
                    'department': tinfo['department'],
                    'designation': tinfo['designation'],
                    'approved_at': timezone.now()
                }
            )
            if created:
                t_user.set_password('Trainer@12345')
                t_user.save()
                TrainerProfile.objects.create(
                    user=t_user,
                    qualifications=tinfo['qualifications'],
                    experience_years=tinfo['experience'],
                    areas_of_expertise=tinfo['expertise'],
                    biography=tinfo['bio']
                )
            trainers[tinfo['username']] = t_user
        self.stdout.write(self.style.SUCCESS("[OK] 3 Certified Trainers verified (password: Trainer@12345)"))

        # 4. EMPLOYEES / LEARNERS
        employees_data = [
            ('emp_arun', 'Arun', 'Kumar', 'arun.kumar@imd.gov.in', 'IMD', "Scientist 'B'", 'EMP-2026-001', 3),
            ('emp_priya', 'Priya', 'Nair', 'priya.nair@incois.gov.in', 'INCOIS', 'Ocean Data Analyst', 'EMP-2026-002', 4),
            ('emp_vikram', 'Vikram', 'Singh', 'vikram.singh@ncmrwf.gov.in', 'NCMRWF', 'HPC Systems Engineer', 'EMP-2026-003', 2),
            ('emp_deepa', 'Deepa', 'Iyer', 'deepa.iyer@iitm.res.in', 'IITM', 'Climate Modeler', 'EMP-2026-004', 5),
            ('emp_rahul', 'Rahul', 'Patel', 'rahul.patel@niot.res.in', 'NIOT', 'Marine Instrumentation Engineer', 'EMP-2026-005', 3),
            ('emp_anita', 'Anita', 'Deshmukh', 'anita.d@imd.gov.in', 'IMD', "Scientist 'C'", 'EMP-2026-006', 6),
            ('emp_suresh', 'Suresh', 'Babu', 'suresh.babu@incois.gov.in', 'INCOIS', 'Ocean Data Analyst', 'EMP-2026-007', 2),
            ('emp_meera', 'Meera', 'Sen', 'meera.sen@iitm.res.in', 'IITM', 'Climate Modeler', 'EMP-2026-008', 4),
            ('emp_kavita', 'Kavita', 'Joshi', 'kavita.j@imd.gov.in', 'IMD', "Scientist 'B'", 'EMP-2026-009', 1),
            ('emp_manish', 'Manish', 'Gupta', 'manish.g@niot.res.in', 'NIOT', 'Marine Instrumentation Engineer', 'EMP-2026-010', 5),
        ]
        employees = {}
        for un, fn, ln, em, dcode, destitle, empid, exp in employees_data:
            e_user, created = User.objects.get_or_create(
                username=un,
                defaults={
                    'first_name': fn,
                    'last_name': ln,
                    'email': em,
                    'role': User.Role.EMPLOYEE,
                    'approval_status': User.ApprovalStatus.APPROVED,
                    'department': depts[dcode],
                    'designation': desigs.get(destitle),
                    'approved_at': timezone.now()
                }
            )
            if created:
                e_user.set_password('Employee@12345')
                e_user.save()
                EmployeeProfile.objects.create(
                    user=e_user,
                    employee_id=empid,
                    experience_years=exp,
                    qualifications="M.Sc. / B.Tech in Physical Sciences or Engineering",
                    areas_of_interest="Climate Modeling, Machine Learning, Remote Sensing",
                    learning_objectives="Advance institutional competencies for national forecasting services."
                )
            employees[un] = e_user
        self.stdout.write(self.style.SUCCESS("[OK] 10 Employees / Learners verified (password: Employee@12345)"))

        # 5. COMPETENCIES
        competencies_data = [
            ("Meteorological Data Analysis", Competency.Domain.SCIENTIFIC, "Statistical and spatial analysis of atmospheric observations and radar data."),
            ("Climate Science", Competency.Domain.SCIENTIFIC, "Understanding coupled atmospheric-oceanic phenomena and global climate projections."),
            ("Remote Sensing", Competency.Domain.SCIENTIFIC, "Processing optical, microwave, and infrared satellite sensor observations."),
            ("GIS", Competency.Domain.TECHNICAL, "Geographic Information Systems for spatial analysis and map creation."),
            ("Oceanographic Modeling", Competency.Domain.SCIENTIFIC, "Hydrodynamic numerical simulation of tides, currents, and ocean temperature."),
            ("Numerical Weather Prediction", Competency.Domain.SCIENTIFIC, "Global and regional atmospheric dynamical modeling systems (WRF, GFS)."),
            ("Artificial Intelligence", Competency.Domain.TECHNICAL, "Fundamentals and principles of intelligent computational systems."),
            ("Machine Learning", Competency.Domain.TECHNICAL, "Supervised and unsupervised algorithms applied to earth observation data."),
            ("Python Programming", Competency.Domain.TECHNICAL, "Python development, scientific stacks (NumPy, SciPy, Xarray, Pandas)."),
            ("Cloud Computing", Competency.Domain.TECHNICAL, "Cloud infrastructure, object storage, and containerized deployment."),
            ("Cybersecurity", Competency.Domain.TECHNICAL, "Information security for critical scientific datasets and cyber resilience."),
            ("Data Analytics", Competency.Domain.TECHNICAL, "Exploratory data analysis and interactive visualization."),
            ("Database Management", Competency.Domain.TECHNICAL, "PostgreSQL, spatial databases (PostGIS), and time-series datastores."),
            ("Environmental Science", Competency.Domain.SCIENTIFIC, "Ecological indicators, air quality modeling, and coastal vulnerability."),
            ("Project Management", Competency.Domain.MANAGERIAL, "Scientific project planning, milestone delivery, and inter-agency coordination."),
        ]
        competencies = {}
        for cname, cdom, cdesc in competencies_data:
            c_obj, _ = Competency.objects.get_or_create(
                name=cname,
                defaults={'domain': cdom, 'description': cdesc}
            )
            competencies[cname] = c_obj
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(competencies)} Competencies loaded in library."))

        # Map Trainer Competencies
        trainer_skill_mappings = [
            ('trainer_climate', 'Climate Science', Proficiency.EXPERT, 14, "Authored 20+ peer-reviewed papers on tropical climate variability."),
            ('trainer_climate', 'Oceanographic Modeling', Proficiency.ADVANCED, 10, "Developed coupled ocean-atmosphere models for cyclone genesis."),
            ('trainer_climate', 'Python Programming', Proficiency.ADVANCED, 9, "Extensive use of Xarray and NetCDF4 for big climate datasets."),
            ('trainer_climate', 'Meteorological Data Analysis', Proficiency.ADVANCED, 12, "MoES monsoon mission data validator."),
            ('trainer_gis', 'Remote Sensing', Proficiency.EXPERT, 11, "Head of satellite data ingest operations at INCOIS."),
            ('trainer_gis', 'GIS', Proficiency.EXPERT, 11, "Expert in QGIS, ArcGIS, and PostGIS for coastal hazard mitigation."),
            ('trainer_gis', 'Environmental Science', Proficiency.ADVANCED, 8, "Marine ecosystem spatial monitoring lead."),
            ('trainer_gis', 'Data Analytics', Proficiency.INTERMEDIATE, 6, "Time-series satellite SST and chlorophyll analytics."),
            ('trainer_ai', 'Artificial Intelligence', Proficiency.EXPERT, 12, "Lead investigator in AI for atmospheric nowcasting."),
            ('trainer_ai', 'Machine Learning', Proficiency.EXPERT, 12, "Deep learning architectures for heavy rainfall event prediction."),
            ('trainer_ai', 'Python Programming', Proficiency.EXPERT, 12, "High-performance Python with CuPy and GPU acceleration."),
            ('trainer_ai', 'Numerical Weather Prediction', Proficiency.ADVANCED, 9, "Hybrid physics-AI numerical weather prediction modules."),
            ('trainer_ai', 'Cloud Computing', Proficiency.ADVANCED, 8, "Deployment of scientific containers on national compute clusters."),
        ]
        for tun, cname, prof, exp, notes in trainer_skill_mappings:
            TrainerCompetency.objects.get_or_create(
                trainer=trainers[tun],
                competency=competencies[cname],
                defaults={'proficiency_level': prof, 'experience_years': exp, 'supporting_description': notes}
            )

        # Map Employee target & current skills
        employee_skills = [
            ('emp_arun', 'Meteorological Data Analysis', Proficiency.INTERMEDIATE, False),
            ('emp_arun', 'Machine Learning', Proficiency.BEGINNER, True),
            ('emp_arun', 'Python Programming', Proficiency.INTERMEDIATE, False),
            ('emp_priya', 'Remote Sensing', Proficiency.INTERMEDIATE, False),
            ('emp_priya', 'Oceanographic Modeling', Proficiency.BEGINNER, True),
            ('emp_priya', 'GIS', Proficiency.ADVANCED, False),
            ('emp_vikram', 'Python Programming', Proficiency.ADVANCED, False),
            ('emp_vikram', 'Artificial Intelligence', Proficiency.INTERMEDIATE, True),
            ('emp_deepa', 'Climate Science', Proficiency.INTERMEDIATE, False),
            ('emp_deepa', 'Numerical Weather Prediction', Proficiency.BEGINNER, True),
        ]
        for eun, cname, prof, is_target in employee_skills:
            EmployeeCompetency.objects.get_or_create(
                employee=employees[eun],
                competency=competencies[cname],
                defaults={'proficiency_level': prof, 'is_target_skill': is_target}
            )

        # 6. COURSE CATEGORIES
        cat_info = [
            ("Atmospheric & Weather Sciences", "weather", "cloud-lightning"),
            ("Oceanography & Marine Technology", "ocean", "waves"),
            ("Data Science & Scientific Computing", "data-science", "database"),
            ("Satellite Remote Sensing & GIS", "remote-sensing", "satellite"),
            ("Climate Dynamics & Modeling", "climate", "globe"),
        ]
        categories = {}
        for cname, cslug, cicon in cat_info:
            cat, _ = Category.objects.get_or_create(name=cname, defaults={'slug': cslug, 'icon_name': cicon})
            categories[cslug] = cat

        # 7. COURSES (8 Comprehensive Courses)
        courses_data = [
            {
                'title': "Applied Meteorological Data Analysis with Python",
                'slug': "applied-meteorological-data-analysis-python",
                'trainer': trainers['trainer_ai'],
                'category': categories['weather'],
                'difficulty': Course.Difficulty.INTERMEDIATE,
                'duration': 14,
                'desc': "Master modern data pipelines for processing raw radiosonde, Doppler radar, and satellite meteorological observations using scientific Python stacks (Xarray, MetPy, and Cartopy).",
                'objectives': "Process radar NetCDF files, compute atmospheric stability indices, and automate automated rainfall forecasts.",
                'prereq': "Basic Python syntax and general atmospheric science concepts.",
                'comp_outcomes': [('Meteorological Data Analysis', Proficiency.ADVANCED), ('Python Programming', Proficiency.ADVANCED)],
                'modules': [
                    ("Module 1: Meteorological Data Formats (GRIB2 & NetCDF4)", "Overview of WMO standard data representations.", [
                        ("Introduction to GRIB2 and NetCDF4 Structures", LearningResource.ResourceType.PDF, "Comprehensive documentation on standard data headers and compression."),
                        ("Python Xarray Data Ingestion Walkthrough", LearningResource.ResourceType.TEXT, "Hands-on guide to loading multidimensional weather data arrays."),
                    ]),
                    ("Module 2: MetPy for Atmospheric Calculations", "Thermodynamic soundings and kinematic wind fields.", [
                        ("Atmospheric Stability Calculation Guide", LearningResource.ResourceType.PDF, "Step-by-step formulas for CAPE, CIN, and Lifted Index."),
                        ("Skew-T / Log-P Diagrams in Python", LearningResource.ResourceType.TEXT, "Code snippets for plotting radiosonde soundings."),
                    ]),
                    ("Module 3: Radar and Precipitation Nowcasting", "Doppler radar reflectivity processing and cell tracking.", [
                        ("Doppler Radar Reflectivity Fundamentals", LearningResource.ResourceType.PDF, "Radar calibration and echo interpretation."),
                        ("Real-time Monsoon Precipitation Notebook", LearningResource.ResourceType.EXTERNAL_LINK, "https://github.com/Unidata/MetPy"),
                    ]),
                ],
                'assessment': {
                    'title': "Applied Meteorological Analysis Certification Exam",
                    'desc': "Official competency assessment covering atmospheric kinematics, GRIB2 processing, and sounding analysis.",
                    'duration': 25,
                    'passing': 60,
                    'questions': [
                        ("What Python library is specially designed for atmospheric and thermodynamic calculations?", ["MetPy", "Scikit-Learn", "Django", "PyGame"], 1),
                        ("Which file format is the standard binary format adopted by WMO for operational meteorological gridded field data?", ["GRIB2", "CSV", "JSON", "XML"], 1),
                        ("In a Skew-T diagram, high values of Convective Available Potential Energy (CAPE) indicate:", ["Severe atmospheric instability and thunderstorm potential", "Completely dry and cloudless conditions", "Freezing surface fog", "Decreased wind shear"], 1),
                        ("Which Xarray function is primary for selecting data along a coordinate dimension?", [".sel()", ".pick()", ".find()", ".query()"], 1),
                    ]
                }
            },
            {
                'title': "Satellite Remote Sensing & GIS for Coastal Hazard Mapping",
                'slug': "remote-sensing-gis-coastal-hazards",
                'trainer': trainers['trainer_gis'],
                'category': categories['remote-sensing'],
                'difficulty': Course.Difficulty.INTERMEDIATE,
                'duration': 16,
                'desc': "Learn satellite imagery analysis, multi-spectral band indices (NDVI, NDWI), and GIS terrain modeling for storm surge, tsunami inundation, and coastal vulnerability mapping.",
                'objectives': "Generate digital elevation models, delineate flood zones, and publish operational web-GIS hazard maps.",
                'prereq': "Basic geography or Earth science fundamentals.",
                'comp_outcomes': [('Remote Sensing', Proficiency.ADVANCED), ('GIS', Proficiency.EXPERT)],
                'modules': [
                    ("Module 1: Multispectral & Synthetic Aperture Radar (SAR)", "Sensor physics and radar penetration.", [
                        ("SAR Imagery Principles for Flood Mapping", LearningResource.ResourceType.PDF, "Sentinel-1 and NISAR radar backscatter analysis."),
                    ]),
                    ("Module 2: Spatial Coastal Vulnerability Assessment", "Integrating elevation, wave runup, and social demographics.", [
                        ("Coastal Hazard Index Methodology", LearningResource.ResourceType.PDF, "MoES INCOIS standard operating guidelines for tsunami inundation mapping."),
                    ]),
                ],
                'assessment': {
                    'title': "Coastal Hazard & GIS Competency Exam",
                    'desc': "Assessment on spatial analysis and remote sensing for marine emergencies.",
                    'duration': 20,
                    'passing': 60,
                    'questions': [
                        ("Which satellite sensor type is capable of acquiring clear imagery through thick cloud cover during cyclones?", ["Synthetic Aperture Radar (SAR)", "Visible Optical Sensor", "Near-Infrared Scanner", "Thermal Hyperspectral Camera"], 1),
                        ("What index is most commonly calculated to delineate open surface water bodies from satellite bands?", ["NDWI (Normalized Difference Water Index)", "NDVI", "NDBI", "NBR"], 1),
                        ("In GIS, which spatial data model represents elevation continuously as a grid of cells?", ["Raster", "Vector Point", "Polyline", "Attribute Table"], 1),
                    ]
                }
            },
            {
                'title': "Coupled Climate Modeling: Monsoons & Climate Change",
                'slug': "coupled-climate-modeling-monsoons",
                'trainer': trainers['trainer_climate'],
                'category': categories['climate'],
                'difficulty': Course.Difficulty.ADVANCED,
                'duration': 20,
                'desc': "Comprehensive study of Earth System Models (ESMs), atmospheric-oceanic coupling physics, and CMIP6 global scenario evaluation for Indian monsoon dynamics.",
                'objectives': "Configure climate runs, analyze teleconnections (ENSO, IOD), and evaluate climate change impact pathways.",
                'prereq': "Fluid dynamics and atmospheric thermodynamics.",
                'comp_outcomes': [('Climate Science', Proficiency.EXPERT), ('Oceanographic Modeling', Proficiency.ADVANCED)],
                'modules': [
                    ("Module 1: Earth System Model Architecture", "Atmosphere, ocean, cryosphere, and land-surface coupling.", [
                        ("Coupled Ocean-Atmosphere Dynamics Lecture Notes", LearningResource.ResourceType.PDF, "Mathematical formulations of primitive Navier-Stokes approximations."),
                    ]),
                    ("Module 2: Monsoon Teleconnections & Decadal Variability", "ENSO, Indian Ocean Dipole, and Madden-Julian Oscillations.", [
                        ("Teleconnections and Indian Summer Monsoon Rainfall", LearningResource.ResourceType.PDF, "Statistical and dynamical relationships of SST anomalies."),
                    ]),
                ],
                'assessment': None
            },
            {
                'title': "Machine Learning for Extreme Weather Forecasting",
                'slug': "machine-learning-extreme-weather",
                'trainer': trainers['trainer_ai'],
                'category': categories['data-science'],
                'difficulty': Course.Difficulty.ADVANCED,
                'duration': 18,
                'desc': "Application of convolutional neural networks (CNNs), Graph Neural Networks (GNNs), and transformer models to numerical weather forecast post-processing and extreme weather nowcasting.",
                'objectives': "Build deep learning pipelines that ingest radar and satellite sequences to predict severe localized precipitation.",
                'prereq': "Python proficiency, linear algebra, and basic neural network knowledge.",
                'comp_outcomes': [('Machine Learning', Proficiency.EXPERT), ('Artificial Intelligence', Proficiency.EXPERT)],
                'modules': [
                    ("Module 1: Data Preparation for Weather AI", "Spatial regridding, normalization, and handling missing radar sweeps.", [
                        ("Weather Data Preprocessing Framework", LearningResource.ResourceType.PDF, "Pipeline architecture for spatiotemporal climate arrays."),
                    ]),
                    ("Module 2: Spatiotemporal Models (ConvLSTM & U-Net)", "Radar echo extrapolation and precipitation nowcasting.", [
                        ("Deep Learning Architectures for Weather Prediction", LearningResource.ResourceType.PDF, "Comparative analysis of U-Net vs Physics-Informed Neural Networks."),
                    ]),
                ],
                'assessment': {
                    'title': "Weather AI Engineering Assessment",
                    'desc': "Evaluation on neural network architectures and loss functions for meteorological nowcasting.",
                    'duration': 20,
                    'passing': 70,
                    'questions': [
                        ("Which neural network architecture is widely used for satellite cloud image segmentation and precipitation prediction?", ["U-Net", "Simple Perceptron", "Word2Vec", "K-Means"], 1),
                        ("Why are standard MSE loss functions often modified with spatial loss (e.g. Critical Success Index) in rain forecasting?", ["Because extreme rainfall events are highly sparse and MSE produces blurry averages", "Because rain cannot be measured numerically", "Because GPU memory cannot compute MSE", "Because radar data is purely text-based"], 1),
                    ]
                }
            },
            {
                'title': "Oceanographic Data Management & Quality Control Standards",
                'slug': "oceanographic-data-management-standards",
                'trainer': trainers['trainer_gis'],
                'category': categories['ocean'],
                'difficulty': Course.Difficulty.BEGINNER,
                'duration': 10,
                'desc': "Standard operating protocols for Argo float data, moored buoy telemetry, and automated real-time quality control flags according to IOC/UNESCO and MoES standards.",
                'objectives': "Perform automated flag assignments, drift detection, and prepare ocean data for archiving.",
                'prereq': "None. Suitable for all incoming technical officers.",
                'comp_outcomes': [('Oceanographic Modeling', Proficiency.INTERMEDIATE), ('Database Management', Proficiency.INTERMEDIATE)],
                'modules': [
                    ("Module 1: Autonomous Ocean Observational Platforms", "Argo floats, gliders, and coastal tide gauges.", [
                        ("Argo Float Telemetry Guide", LearningResource.ResourceType.PDF, "Data packet decoding and satellite transmission protocols."),
                    ]),
                ],
                'assessment': None
            },
            {
                'title': "Numerical Weather Prediction: WRF Model Configuration & Execution",
                'slug': "numerical-weather-prediction-wrf-model",
                'trainer': trainers['trainer_climate'],
                'category': categories['weather'],
                'difficulty': Course.Difficulty.ADVANCED,
                'duration': 22,
                'desc': "Hands-on installation, WPS domain nesting, physics parameterization, and distributed MPI parallel execution of the Weather Research and Forecasting (WRF) model.",
                'objectives': "Configure regional WRF model domains, generate boundary conditions, and run high-resolution cyclone forecasts.",
                'prereq': "Linux command line, MPI fundamentals, and meteorological dynamics.",
                'comp_outcomes': [('Numerical Weather Prediction', Proficiency.EXPERT)],
                'modules': [
                    ("Module 1: WRF Preprocessing System (WPS)", "Geogrid, ungrib, and metgrid utilities.", [
                        ("WRF Modeling System User Manual", LearningResource.ResourceType.PDF, "Domain setup, projection selection, and topographical datasets."),
                    ]),
                ],
                'assessment': None
            },
            {
                'title': "PostgreSQL & Spatial PostGIS for Earth Science Data",
                'slug': "postgresql-postgis-earth-science",
                'trainer': trainers['trainer_ai'],
                'category': categories['data-science'],
                'difficulty': Course.Difficulty.INTERMEDIATE,
                'duration': 12,
                'desc': "Design relational schemas and spatial database geometries for earthquake catalogs, meteorological station networks, and ocean cruise observations.",
                'objectives': "Execute complex spatial joins, nearest-neighbor queries, and index optimization for millions of geospatial points.",
                'prereq': "Basic SQL knowledge.",
                'comp_outcomes': [('Database Management', Proficiency.ADVANCED), ('GIS', Proficiency.ADVANCED)],
                'modules': [
                    ("Module 1: Spatial Types & Indexing (R-Tree / GIST)", "Geometry vs Geography types in PostgreSQL.", [
                        ("PostGIS Spatial Schema Optimization", LearningResource.ResourceType.PDF, "Guide to spatial query performance and spatial indexes."),
                    ]),
                ],
                'assessment': None
            },
            {
                'title': "Institutional Leadership & Scientific Project Governance",
                'slug': "institutional-leadership-scientific-project-governance",
                'trainer': admin_user,
                'category': categories['weather'],
                'difficulty': Course.Difficulty.BEGINNER,
                'duration': 8,
                'desc': "Administrative protocols, public financial management, inter-institutional collaboration, and capacity building frameworks under MoES central guidelines.",
                'objectives': "Execute GFR rules, oversee multidisciplinary science missions, and report to parliamentary committees.",
                'prereq': "None. Recommended for all scientific officers.",
                'comp_outcomes': [('Project Management', Proficiency.ADVANCED)],
                'modules': [
                    ("Module 1: Science Governance & Financial Guidelines", "Public procurement and project review cycles.", [
                        ("MoES Administrative Governance Manual", LearningResource.ResourceType.PDF, "Standard operating procedures for central organizational projects."),
                    ]),
                ],
                'assessment': None
            },
        ]

        created_courses = {}
        for cdata in courses_data:
            course, _ = Course.objects.get_or_create(
                slug=cdata['slug'],
                defaults={
                    'title': cdata['title'],
                    'trainer': cdata['trainer'],
                    'category': cdata['category'],
                    'difficulty_level': cdata['difficulty'],
                    'estimated_duration_hours': cdata['duration'],
                    'description': cdata['desc'],
                    'learning_objectives': cdata['objectives'],
                    'prerequisites': cdata['prereq'],
                    'status': Course.Status.PUBLISHED,
                }
            )
            created_courses[cdata['slug']] = course

            # Course competencies
            for comp_name, target_prof in cdata['comp_outcomes']:
                CourseCompetency.objects.get_or_create(
                    course=course,
                    competency=competencies[comp_name],
                    defaults={'target_proficiency': target_prof}
                )

            # Modules & Resources
            for order_idx, (m_title, m_desc, res_list) in enumerate(cdata['modules'], 1):
                mod, _ = CourseModule.objects.get_or_create(
                    course=course,
                    order=order_idx,
                    defaults={'title': m_title, 'description': m_desc, 'is_mandatory': True}
                )
                for r_idx, (r_title, r_type, r_notes) in enumerate(res_list, 1):
                    LearningResource.objects.get_or_create(
                        module=mod,
                        order=r_idx,
                        defaults={
                            'title': r_title,
                            'resource_type': r_type,
                            'text_content': r_notes if r_type != LearningResource.ResourceType.EXTERNAL_LINK else '',
                            'external_url': r_notes if r_type == LearningResource.ResourceType.EXTERNAL_LINK else '',
                        }
                    )

            # Assessment
            if cdata['assessment']:
                ass_info = cdata['assessment']
                assessment, _ = Assessment.objects.get_or_create(
                    course=course,
                    defaults={
                        'title': ass_info['title'],
                        'description': ass_info['desc'],
                        'duration_minutes': ass_info['duration'],
                        'passing_percentage': ass_info['passing'],
                        'max_attempts': 3,
                        'is_published': True,
                    }
                )
                for q_idx, (q_text, opts, correct_idx) in enumerate(ass_info['questions'], 1):
                    q, _ = Question.objects.get_or_create(
                        assessment=assessment,
                        order=q_idx,
                        defaults={'question_text': q_text, 'marks': 1}
                    )
                    for o_idx, opt_text in enumerate(opts, 1):
                        AnswerOption.objects.get_or_create(
                            question=q,
                            order=o_idx,
                            defaults={'option_text': opt_text, 'is_correct': (o_idx == correct_idx)}
                        )

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(created_courses)} Comprehensive Courses with modules and assessments established."))

        # 8. ENROLLMENTS & LEARNER JOURNEYS
        c_applied = created_courses['applied-meteorological-data-analysis-python']
        c_hazard = created_courses['remote-sensing-gis-coastal-hazards']

        # Arun Kumar: Completed Applied Met course, passed exam, earned Certificate!
        enr_arun, _ = Enrollment.objects.get_or_create(
            employee=employees['emp_arun'],
            course=c_applied,
            defaults={'progress_percentage': 100.0, 'is_completed': True, 'completed_at': timezone.now() - timedelta(days=2)}
        )
        for m in c_applied.modules.all():
            ModuleProgress.objects.get_or_create(
                enrollment=enr_arun,
                module=m,
                defaults={'is_completed': True, 'completed_at': timezone.now() - timedelta(days=3)}
            )
        # Arun passed assessment
        ass_applied = c_applied.assessment
        att_arun, _ = AssessmentAttempt.objects.get_or_create(
            assessment=ass_applied,
            employee=employees['emp_arun'],
            attempt_number=1,
            defaults={
                'total_marks': 4.0,
                'score_obtained': 4.0,
                'percentage_obtained': 100.0,
                'passed': True,
                'submitted_at': timezone.now() - timedelta(days=2)
            }
        )
        # Arun certificate
        issue_certificate_if_eligible(enr_arun)

        # Priya Nair: Completed Hazard Mapping course, earned certificate
        enr_priya, _ = Enrollment.objects.get_or_create(
            employee=employees['emp_priya'],
            course=c_hazard,
            defaults={'progress_percentage': 100.0, 'is_completed': True, 'completed_at': timezone.now() - timedelta(days=5)}
        )
        for m in c_hazard.modules.all():
            ModuleProgress.objects.get_or_create(
                enrollment=enr_priya,
                module=m,
                defaults={'is_completed': True, 'completed_at': timezone.now() - timedelta(days=5)}
            )
        ass_hazard = c_hazard.assessment
        AssessmentAttempt.objects.get_or_create(
            assessment=ass_hazard,
            employee=employees['emp_priya'],
            attempt_number=1,
            defaults={
                'total_marks': 3.0,
                'score_obtained': 3.0,
                'percentage_obtained': 100.0,
                'passed': True,
                'submitted_at': timezone.now() - timedelta(days=5)
            }
        )
        issue_certificate_if_eligible(enr_priya)

        # Vikram Singh: In progress on Applied Met (66% complete)
        enr_vikram, _ = Enrollment.objects.get_or_create(
            employee=employees['emp_vikram'],
            course=c_applied,
            defaults={'progress_percentage': 66.7, 'is_completed': False}
        )
        mods_applied = list(c_applied.modules.all())
        if len(mods_applied) >= 2:
            ModuleProgress.objects.get_or_create(enrollment=enr_vikram, module=mods_applied[0], defaults={'is_completed': True, 'completed_at': timezone.now() - timedelta(days=1)})
            ModuleProgress.objects.get_or_create(enrollment=enr_vikram, module=mods_applied[1], defaults={'is_completed': True, 'completed_at': timezone.now() - timedelta(hours=8)})
            ModuleProgress.objects.get_or_create(enrollment=enr_vikram, module=mods_applied[2], defaults={'is_completed': False})

        # Deepa Iyer & other employees enrollments
        for emp_key in ['emp_deepa', 'emp_rahul', 'emp_anita', 'emp_suresh']:
            Enrollment.objects.get_or_create(
                employee=employees[emp_key],
                course=c_applied,
                defaults={'progress_percentage': 33.3, 'is_completed': False}
            )
            Enrollment.objects.get_or_create(
                employee=employees[emp_key],
                course=c_hazard,
                defaults={'progress_percentage': 50.0, 'is_completed': False}
            )

        self.stdout.write(self.style.SUCCESS("[OK] Active enrollments, real progress calculations, and verified certificates seeded."))

        # 9. COURSE FEEDBACK
        CourseFeedback.objects.get_or_create(
            course=c_applied,
            employee=employees['emp_arun'],
            defaults={
                'course_rating': 5,
                'trainer_rating': 5,
                'comments': "Exceptional course! Hands-on Xarray and MetPy scripts immediately elevated our operational radar workflows at IMD.",
                'improvement_suggestions': "Include a live case study on severe convective squall lines."
            }
        )
        CourseFeedback.objects.get_or_create(
            course=c_hazard,
            employee=employees['emp_priya'],
            defaults={
                'course_rating': 5,
                'trainer_rating': 5,
                'comments': "The SAR radar flood delineations are directly applicable to our INCOIS coastal early warning alerts.",
                'improvement_suggestions': "Add more high-resolution bathymetric datasets."
            }
        )

        # 10. ANNOUNCEMENTS
        Announcement.objects.get_or_create(
            title="Launch of MoES National Capacity Building Portal 2026",
            defaults={
                'author': admin_user,
                'announcement_type': Announcement.Type.GENERAL,
                'is_public': True,
                'is_pinned': True,
                'content': "Capacity Connect is officially operational across all MoES autonomous institutes (IMD, INCOIS, NCMRWF, IITM, NIOT). Employees can now discover mentors, build verified competencies, and earn accredited certifications."
            }
        )
        Announcement.objects.get_or_create(
            title="Special Training Batch: Monsoon 2026 Numerical Weather Prediction",
            defaults={
                'author': admin_user,
                'announcement_type': Announcement.Type.TRAINING,
                'is_public': True,
                'is_pinned': False,
                'content': "Admissions open for the upcoming cohort on coupled high-resolution WRF modeling. Nominated scientists should enroll before end of month."
            }
        )

        # 11. KNOWLEDGE LIBRARY RESOURCES
        TrainerResource.objects.get_or_create(
            title="Indian Ocean Tsunami Early Warning Standard Operating Procedure (SOP)",
            defaults={
                'uploaded_by': trainers['trainer_gis'],
                'category': TrainerResource.Category.MANUAL,
                'description': "Official INCOIS procedural manual on seismic trigger analysis, ocean buoy verification, and coastal evacuation dissemination.",
                'external_link': "https://incois.gov.in"
            }
        )
        TrainerResource.objects.get_or_create(
            title="Deep Learning for Atmospheric Nowcasting: Technical Review Paper",
            defaults={
                'uploaded_by': trainers['trainer_ai'],
                'category': TrainerResource.Category.RESEARCH_PAPER,
                'description': "Survey paper comparing ConvLSTM, PredRNN, and Graph Neural Networks for meteorological nowcasting.",
                'external_link': "https://ncmrwf.gov.in"
            }
        )

        # 12. NOTIFICATIONS
        Notification.objects.get_or_create(
            user=employees['emp_arun'],
            title="Certificate Issued!",
            defaults={
                'notification_type': Notification.Type.CERTIFICATE,
                'message': "Your Certificate of Completion for 'Applied Meteorological Data Analysis with Python' is now available for download.",
                'target_url': "/certificates/verify/",
                'is_read': False,
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] Announcements, Centralized Resources, and In-App Notifications initialized."))
        self.stdout.write(self.style.SUCCESS("\n======================================================="))
        self.stdout.write(self.style.SUCCESS("CAPACITY CONNECT DEMO ENVIRONMENT READY! (SIH26075)"))
        self.stdout.write(self.style.SUCCESS("======================================================="))
        self.stdout.write("Demo Credentials:")
        self.stdout.write("  Admin:     admin / Admin@12345")
        self.stdout.write("  Trainer:   trainer_ai / Trainer@12345 (or trainer_climate, trainer_gis)")
        self.stdout.write("  Employee:  emp_arun / Employee@12345 (or emp_priya, emp_vikram)")
        self.stdout.write("=======================================================\n")
