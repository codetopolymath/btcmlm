from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Earning, Withdrawal, Package, Purchase
from django.db import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'sponsor', 'sponsor_address', 'level', 'total_earnings', 'available_balance', 'wallet_address')
        read_only_fields = ('level', 'total_earnings', 'available_balance')

class UserRegistrationSerializer(serializers.ModelSerializer):
    sponsor_address = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'sponsor_address', 'wallet_address')

    def create(self, validated_data):
        sponsor_address = validated_data.pop('sponsor_address')
        sponsor = User.objects.filter(models.Q(email=sponsor_address) | models.Q(wallet_address=sponsor_address)).first()
        if not sponsor:
            raise serializers.ValidationError("Invalid sponsor address")
        user = User.objects.create_user(sponsor=sponsor, **validated_data)
        return user

class EarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earning
        fields = '__all__'

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = '__all__'

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'level', 'total_earnings')

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'package', 'timestamp']
        read_only_fields = ['user', 'timestamp']  # Make user read-only

    def create(self, validated_data):
        # The user will be set in the view, so we don't need it here
        return Purchase.objects.create(**validated_data)