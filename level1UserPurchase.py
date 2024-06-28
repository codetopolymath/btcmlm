# random_level1_purchase.py

import os
import django
import random
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'btc_mlm_backend.settings')
django.setup()

from mlm_users.models import User, Package, Purchase
from django.db.models import F

def make_random_level1_purchase():
    # Get all level 1 users
    level1_users = User.objects.filter(level=1)

    if not level1_users.exists():
        print("No level 1 users found.")
        return

    # Select a random level 1 user
    random_user = random.choice(level1_users)

    # Get all available packages
    packages = Package.objects.all()

    if not packages.exists():
        print("No packages available.")
        return

    # Select a random package
    random_package = random.choice(packages)

    # Create the purchase
    purchase = Purchase.objects.create(user=random_user, package=random_package)

    # Distribute profit
    purchase.distribute_profit()

    # Refresh the user instance to get updated balances
    random_user.refresh_from_db()

    print(f"Purchase made successfully!")
    print(f"User: {random_user.username} (Email: {random_user.email})")
    print(f"Package: {random_package.name} (Price: ${random_package.price})")
    print(f"User's new total earnings: ${random_user.total_earnings}")
    print(f"User's new available balance: ${random_user.available_balance}")

    # Print sponsor's earnings if exists
    if random_user.sponsor:
        random_user.sponsor.refresh_from_db()
        print(f"Sponsor's ({random_user.sponsor.username}) new total earnings: ${random_user.sponsor.total_earnings}")

if __name__ == '__main__':
    make_random_level1_purchase()