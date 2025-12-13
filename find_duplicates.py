
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pharmacy.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

def find_duplicates():
    print("Checking for duplicate users...")
    duplicates = User.objects.values('email').annotate(email_count=Count('email')).filter(email_count__gt=1)

    if not duplicates:
        print("No duplicate users found.")
        return

    for entry in duplicates:
        email = entry['email']
        print(f"\nFound {entry['email_count']} users with email: {email}")
        users = User.objects.filter(email__iexact=email).order_by('-last_login')
        
        for user in users:
            print(f"  - ID: {user.id}, Username: {user.username}, Last Login: {user.last_login}, Date Joined: {user.date_joined}")

if __name__ == "__main__":
    find_duplicates()
