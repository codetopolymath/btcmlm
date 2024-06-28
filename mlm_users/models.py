from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from decimal import Decimal

class User(AbstractUser):
    sponsor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sponsored_users')
    sponsor_address = models.CharField(_("Sponsor's Address"), max_length=255, blank=True)
    level = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    email = models.EmailField(unique=True)
    wallet_address = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username

    def clean(self):
        if self.sponsor:
            if self.sponsor == self:
                raise ValidationError("A user cannot be their own sponsor.")
            if self.is_ancestor(self.sponsor):
                raise ValidationError("Circular sponsorship is not allowed.")

    def save(self, *args, **kwargs):
        if self.sponsor:
            try:
                self.clean()
                self.level = self.sponsor.level + 1
            except ValidationError:
                if self.pk:
                    self.sponsor = User.objects.get(pk=self.pk).sponsor
                else:
                    self.sponsor = None
                self.level = 0 if self.sponsor is None else self.sponsor.level + 1
        super().save(*args, **kwargs)

    def is_ancestor(self, user):
        if not user:
            return False
        if user == self:
            return True
        return self.is_ancestor(user.sponsor)

    def update_levels(self):
        for user in self.sponsored_users.all():
            user.level = self.level + 1
            user.save()
            user.update_levels()

    def get_team(self, levels=2):
        team = []
        queue = [(self, 0)]
        while queue:
            user, current_level = queue.pop(0)
            if current_level < levels:
                sponsored = user.sponsored_users.all()
                team.extend(sponsored)
                queue.extend((sponsored_user, current_level + 1) for sponsored_user in sponsored)
        return team

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created and instance.sponsor:
        instance.update_levels()

class Package(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 40.00 for 40%

    def __str__(self):
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"

    def distribute_profit(self):
        profit = self.package.price * (self.package.profit_percentage / Decimal('100'))
        sponsor = self.user.sponsor
        if sponsor:
            sponsor_earning = profit * Decimal('0.30')
            Earning.objects.create(user=sponsor, amount=sponsor_earning, description=f"Profit from {self.user.username}'s purchase of {self.package.name}")
            sponsor.total_earnings += sponsor_earning
            sponsor.available_balance += sponsor_earning
            sponsor.save()

            grand_sponsor = sponsor.sponsor
            if grand_sponsor:
                grand_sponsor_earning = profit * Decimal('0.10')
                Earning.objects.create(user=grand_sponsor, amount=grand_sponsor_earning, description=f"Profit from {self.user.username}'s purchase of {self.package.name}")
                grand_sponsor.total_earnings += grand_sponsor_earning
                grand_sponsor.available_balance += grand_sponsor_earning
                grand_sponsor.save()

class Earning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('rejected', 'Rejected')])
    timestamp = models.DateTimeField(auto_now_add=True)