# store/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_username, user_email
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Auto-link social account to existing user with same email.
        """
        email = sociallogin.account.extra_data.get("email")
        if not email:
            return

        try:
            existing_user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return  # No existing user, will create new

        # Connect social account to existing user
        if not sociallogin.is_existing:
            sociallogin.connect(request, existing_user)

    def populate_user(self, request, sociallogin, data):
        """
        Populate username from email if missing.
        """
        user = super().populate_user(request, sociallogin, data)
        if not user_username(user) and data.get("email"):
            user.username = data["email"].split("@")[0]
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Allow auto signup/login without intermediate page.
        """
        return True

    def get_login_redirect_url(self, request):
        """
        Redirect users to dashboard after login.
        """
        return resolve_url("/dashboard/")

    def save_user(self, request, sociallogin, form=None):
        """
        Save user immediately after successful social login.
        """
        user = sociallogin.user
        user.set_unusable_password()  # Prevent empty password login
        user.save()
        sociallogin.save(request)
        return user
