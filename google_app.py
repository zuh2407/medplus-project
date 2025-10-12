import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Get Site object
site = Site.objects.get(id=int(os.getenv("DJANGO_SITE_ID", "1")))

# Get credentials from .env
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

if client_id and client_secret:
    app, created = SocialApp.objects.update_or_create(
        provider="google",
        name="Google",
        defaults={"client_id": client_id, "secret": client_secret},
    )
    app.sites.add(site)
    print("✅ Google SocialApp created or updated successfully")
else:
    print("❌ Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
