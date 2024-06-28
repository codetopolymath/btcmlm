# tests.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import User, Package, Purchase, Earning, Withdrawal

class UserModelTests(TestCase):
    def setUp(self):
        self.root_user = User.objects.create_user(username='root', email='root@example.com', password='rootpassword')

    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.assertEqual(user.level, 0)
        self.assertEqual(user.total_earnings, Decimal('0.00'))
        self.assertEqual(user.available_balance, Decimal('0.00'))

    def test_sponsorship(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password', sponsor=self.root_user)
        self.assertEqual(user1.level, 1)
        self.assertEqual(user1.sponsor, self.root_user)

    def test_circular_sponsorship_prevention(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password', sponsor=self.root_user)
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password', sponsor=user1)
        
        # Attempt to create a circular sponsorship
        self.root_user.sponsor = user2
        self.root_user.save()
        self.root_user.refresh_from_db()
        
        # The sponsorship should not have changed
        self.assertIsNone(self.root_user.sponsor)

    def test_get_team(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password', sponsor=self.root_user)
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password', sponsor=self.root_user)
        user1_1 = User.objects.create_user(username='user1_1', email='user1_1@example.com', password='password', sponsor=user1)
        
        team = self.root_user.get_team()
        self.assertEqual(len(team), 3)
        self.assertIn(user1, team)
        self.assertIn(user2, team)
        self.assertIn(user1_1, team)

    def test_update_levels(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password', sponsor=self.root_user)
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password', sponsor=user1)
        user3 = User.objects.create_user(username='user3', email='user3@example.com', password='password', sponsor=user2)
        
        self.assertEqual(user1.level, 1)
        self.assertEqual(user2.level, 2)
        self.assertEqual(user3.level, 3)

class PackageModelTests(TestCase):
    def test_package_creation(self):
        package = Package.objects.create(name='Test Package', price=100.00, profit_percentage=40.00)
        self.assertEqual(str(package), 'Test Package')

class PurchaseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.package = Package.objects.create(name='Test Package', price=100.00, profit_percentage=40.00)

    def test_purchase_creation(self):
        purchase = Purchase.objects.create(user=self.user, package=self.package)
        self.assertEqual(str(purchase), 'testuser - Test Package')

    def test_profit_distribution(self):
        sponsor = User.objects.create_user(username='sponsor', email='sponsor@example.com', password='sponsorpassword')
        grand_sponsor = User.objects.create_user(username='grand_sponsor', email='grand_sponsor@example.com', password='grandpassword')
        
        self.user.sponsor = sponsor
        self.user.save()
        sponsor.sponsor = grand_sponsor
        sponsor.save()

        purchase = Purchase.objects.create(user=self.user, package=self.package)
        purchase.distribute_profit()

        sponsor.refresh_from_db()
        grand_sponsor.refresh_from_db()

        self.assertEqual(sponsor.total_earnings, Decimal('12.00'))  # 30% of 40% of 100
        self.assertEqual(grand_sponsor.total_earnings, Decimal('4.00'))  # 10% of 40% of 100

class EarningModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_earning_creation(self):
        earning = Earning.objects.create(user=self.user, amount=50.00, description='Test earning')
        self.assertEqual(earning.user, self.user)
        self.assertEqual(earning.amount, Decimal('50.00'))

class WithdrawalModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_withdrawal_creation(self):
        withdrawal = Withdrawal.objects.create(user=self.user, amount=25.00, status='pending')
        self.assertEqual(withdrawal.user, self.user)
        self.assertEqual(withdrawal.amount, Decimal('25.00'))
        self.assertEqual(withdrawal.status, 'pending')