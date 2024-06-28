# mlm_users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Earning, Withdrawal, Package, Purchase

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'sponsor', 'level', 'total_earnings', 'available_balance')
    list_filter = ('level',)
    search_fields = ('username', 'email', 'sponsor__username')
    fieldsets = UserAdmin.fieldsets + (
        ('MLM Info', {'fields': ('sponsor', 'sponsor_address', 'level', 'total_earnings', 'available_balance', 'wallet_address')}),
    )

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'description')

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('user__username',)

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'profit_percentage')
    search_fields = ('name',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'package__name')