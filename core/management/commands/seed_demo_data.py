import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from donors.models import Donor
from blood_requests.models import BloodRequest
from core.models import Testimonial, FAQ

FIRST_NAMES = ['Rahim', 'Karim', 'Fatima', 'Ayesha', 'Sabbir', 'Nusrat', 'Tanvir', 'Mim',
               'Hasan', 'Ridika', 'Arif', 'Shanta', 'Imran', 'Lamia', 'Nayeem', 'Priya']
LAST_NAMES = ['Islam', 'Ahmed', 'Rahman', 'Hossain', 'Chowdhury', 'Akter', 'Khan', 'Talukder']
DIVISIONS_DISTRICTS = {
    'Dhaka': ['Faridpur', 'Gazipur', 'Narayanganj', 'Dhaka'],
    'Chattogram': ['Cumilla', 'Cox\'s Bazar', 'Chattogram'],
    'Rajshahi': ['Bogura', 'Pabna', 'Rajshahi'],
    'Khulna': ['Jessore', 'Khulna'],
    'Sylhet': ['Sylhet', 'Moulvibazar'],
}
BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
HOSPITALS = ['Dhaka Medical College Hospital', 'Square Hospital', 'Faridpur Medical College',
             'Ibn Sina Hospital', 'United Hospital', 'Chattogram Medical College Hospital']


class Command(BaseCommand):
    help = 'Seeds the database with realistic demo donors, blood requests, testimonials, and FAQs.'

    def add_arguments(self, parser):
        parser.add_argument('--donors', type=int, default=24)
        parser.add_argument('--requests', type=int, default=15)

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')
        self._seed_donors(options['donors'])
        self._seed_requests(options['requests'])
        self._seed_testimonials()
        self._seed_faqs()
        self.stdout.write(self.style.SUCCESS('Done. Log in as any seeded user with password: DemoPass123'))

    def _seed_donors(self, n):
        created = 0
        for i in range(n):
            first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
            username = f'{first.lower()}{i}'
            email = f'{username}@example.com'
            if User.objects.filter(email=email).exists():
                continue
            user = User.objects.create_user(
                username=username, email=email, password='DemoPass123',
                first_name=first, last_name=last, user_type='donor',
                phone_number=f'+8801{random.randint(100000000, 999999999)}',
            )
            division = random.choice(list(DIVISIONS_DISTRICTS.keys()))
            district = random.choice(DIVISIONS_DISTRICTS[division])
            Donor.objects.create(
                user=user,
                age=random.randint(18, 55),
                gender=random.choice(['M', 'F']),
                blood_group=random.choice(BLOOD_GROUPS),
                division=division,
                district=district,
                area=f'{district} Sadar',
                address=f'House {random.randint(1,200)}, Road {random.randint(1,20)}, {district}',
                last_donation_date=timezone.now().date() - timedelta(days=random.randint(0, 400)) if random.random() > 0.3 else None,
                is_available=random.random() > 0.2,
                is_featured=random.random() > 0.85,
                weight=random.randint(45, 90),
                occupation=random.choice(['Student', 'Engineer', 'Teacher', 'Business', 'Doctor', '']),
                total_donations=random.randint(0, 12),
            )
            created += 1
        self.stdout.write(f'  {created} donors created')

    def _seed_requests(self, n):
        requesters = list(User.objects.all())
        if not requesters:
            self.stdout.write(self.style.WARNING('  No users found — seed donors first.'))
            return
        created = 0
        for i in range(n):
            BloodRequest.objects.create(
                requested_by=random.choice(requesters),
                patient_name=f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}',
                hospital=random.choice(HOSPITALS),
                blood_group_needed=random.choice(BLOOD_GROUPS),
                units_needed=random.randint(1, 4),
                urgency=random.choice(['normal', 'urgent', 'emergency']),
                required_date=timezone.now().date() + timedelta(days=random.randint(0, 10)),
                location=random.choice([d for districts in DIVISIONS_DISTRICTS.values() for d in districts]),
                contact_person=f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}',
                contact_phone=f'+8801{random.randint(100000000, 999999999)}',
                description='Seeded demo request for testing the platform.',
                status=random.choice(['open', 'open', 'open', 'accepted', 'completed']),
            )
            created += 1
        self.stdout.write(f'  {created} blood requests created')

    def _seed_testimonials(self):
        if Testimonial.objects.exists():
            return
        samples = [
            ('Rahim Islam', 'Regular Donor', 'Blood Finder connected me with a hospital just 10 minutes from home. Donating has never been this easy.'),
            ('Ayesha Rahman', "Patient's Family", 'We found a matching donor within an hour during an emergency. This platform is a lifesaver — literally.'),
            ('Tanvir Ahmed', 'Blood Donor', 'The dashboard makes it simple to track my donation history and see who I have helped.'),
        ]
        for name, role, message in samples:
            Testimonial.objects.create(name=name, role=role, message=message, rating=5)
        self.stdout.write('  3 testimonials created')

    def _seed_faqs(self):
        if FAQ.objects.exists():
            return
        faqs = [
            ('Who can donate blood?', 'Most healthy adults aged 18-65 weighing at least 45kg can donate, roughly every 90 days.'),
            ('Is my personal information safe?', 'Your contact details are only shown to logged-in members, and you control your availability status at any time.'),
            ('How fast can I find a donor in an emergency?', 'Use the search filters for blood group and location — marking a request as "Emergency" also notifies matching donors instantly.'),
            ('Do I need to pay to use Blood Finder?', 'No. Blood Finder is a free community platform connecting donors and recipients.'),
        ]
        for i, (q, a) in enumerate(faqs):
            FAQ.objects.create(question=q, answer=a, order=i)
        self.stdout.write('  4 FAQs created')
