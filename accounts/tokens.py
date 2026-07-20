from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Same uidb64+token pattern Django uses for password reset, reused for
    "verify your email" links. Hashing in is_email_verified means a token
    stops working the moment it's been used once.
    """
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_email_verified}"


email_verification_token = EmailVerificationTokenGenerator()
