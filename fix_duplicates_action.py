
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

def fix_duplicates():
    print("Fixing duplicate users...")
    duplicates = User.objects.values('email').annotate(email_count=Count('email')).filter(email_count__gt=1)

    if not duplicates:
        print("No duplicate users found.")
        return

    for entry in duplicates:
        email = entry['email']
        print(f"\nProcessing email: {email}")
        users = list(User.objects.filter(email__iexact=email).order_by('-last_login'))
        
        # Keep the first one (most recent login), delete the rest
        user_to_keep = users[0]
        users_to_delete = users[1:]
        
        print(f"  Keeping user: ID {user_to_keep.id} ({user_to_keep.username})")
        
        for user in users_to_delete:
            print(f"  Deleting user: ID {user.id} ({user.username})")
            user.delete()
            
    print("\nDuplicate cleanup complete.")

if __name__ == "__main__":
    fix_duplicates()
