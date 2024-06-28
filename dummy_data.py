# dummy_data.py

import os
import django
import random
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'btc_mlm_backend.settings')
django.setup()

from mlm_users.models import User, Package, Purchase, Earning, Withdrawal

def create_user(username, email, sponsor=None):
    return User.objects.create_user(
        username=username,
        email=email,
        password='password123',
        sponsor=sponsor,
        wallet_address=f'0x{random.randint(0, 16**40):040x}'
    )

def create_dummy_data():
    # Create Packages
    packages = [
        Package.objects.create(name='Bronze Package', price=99.99, profit_percentage=20.00),
        Package.objects.create(name='Silver Package', price=299.99, profit_percentage=30.00),
        Package.objects.create(name='Gold Package', price=599.99, profit_percentage=40.00),
        Package.objects.create(name='Platinum Package', price=999.99, profit_percentage=50.00),
        Package.objects.create(name='Diamond Package', price=1999.99, profit_percentage=60.00),
    ]

    # Create Users
    root_user = create_user('johndoe', 'johndoe@example.com')
    
    all_users = [root_user]
    current_level_users = [root_user]
    
    # Create 6 levels of users
    for level in range(1, 7):
        next_level_users = []
        for user in current_level_users:
            # Create 3-5 sponsored users for each user in the current level
            for i in range(random.randint(3, 5)):
                new_user = create_user(
                    f'{user.username}_sub{level}_{i+1}',
                    f'{user.username}_sub{level}_{i+1}@example.com',
                    sponsor=user
                )
                next_level_users.append(new_user)
                all_users.append(new_user)
        current_level_users = next_level_users
        print(f"Created {len(next_level_users)} users at level {level}")

    # Create Purchases
    for user in all_users:
        for _ in range(random.randint(1, 3)):
            package = random.choice(packages)
            purchase = Purchase.objects.create(user=user, package=package)
            purchase.distribute_profit()

    # Create some Withdrawals
    for user in random.sample(all_users, min(len(all_users) // 2, 100)):  # Create withdrawals for up to 100 users or half of all users, whichever is smaller
        amount = Decimal(random.uniform(10, 500)).quantize(Decimal('0.01'))
        Withdrawal.objects.create(user=user, amount=amount, status=random.choice(['pending', 'completed', 'rejected']))

    print(f"Dummy data created successfully! Total users: {len(all_users)}")

    # Print some sample users for easy testing
    print("\nSample users for testing:")
    for level in range(7):
        sample_user = random.choice([u for u in all_users if u.level == level])
        print(f"Level {level}: {sample_user.email}")

if __name__ == '__main__':
    create_dummy_data()