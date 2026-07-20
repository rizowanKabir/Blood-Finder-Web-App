"""
Shared constants used across apps. Centralised here so blood groups,
divisions, and similar choice lists never drift out of sync between
the donors, blood_requests, and accounts apps.
"""

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

# Bangladesh's 8 administrative divisions. District/Area are left as free
# text (rather than a second hard-coded choice list) so the app isn't
# locked to a hand-maintained district table — trivial to swap for a
# proper Division -> District -> Upazila fixture/model later if needed.
DIVISION_CHOICES = [
    ('Barishal', 'Barishal'),
    ('Chattogram', 'Chattogram'),
    ('Dhaka', 'Dhaka'),
    ('Khulna', 'Khulna'),
    ('Mymensingh', 'Mymensingh'),
    ('Rajshahi', 'Rajshahi'),
    ('Rangpur', 'Rangpur'),
    ('Sylhet', 'Sylhet'),
]

USER_TYPE_CHOICES = [
    ('user', 'Normal User'),
    ('donor', 'Blood Donor'),
]

MIN_DONOR_AGE = 18
MAX_DONOR_AGE = 65
MIN_DONOR_WEIGHT_KG = 45
DONATION_ELIGIBILITY_GAP_DAYS = 90  # standard ~3 month gap between whole-blood donations
