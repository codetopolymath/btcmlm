from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from .models import User, Earning, Withdrawal, Package, Purchase
from .serializers import UserSerializer, UserRegistrationSerializer, EarningSerializer, WithdrawalSerializer, TeamMemberSerializer, PackageSerializer, PurchaseSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response({'error': 'Validation Error', 'details': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Registration failed', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def profile(self, request):
        try:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to retrieve profile', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def earnings(self, request):
        try:
            earnings = request.user.earnings.all()
            serializer = EarningSerializer(earnings, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to retrieve earnings', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def withdrawals(self, request):
        try:
            withdrawals = request.user.withdrawals.all()
            serializer = WithdrawalSerializer(withdrawals, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to retrieve withdrawals', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def team(self, request):
        try:
            team = request.user.get_team(levels=2)
            serializer = TeamMemberSerializer(team, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to retrieve team', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EarningViewSet(viewsets.ModelViewSet):
    queryset = Earning.objects.all()
    serializer_class = EarningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(user=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to retrieve earnings', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            amount = request.data.get('amount')
            if user.available_balance < float(amount):
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
            return super().create(request, *args, **kwargs)
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Withdrawal request failed', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(user=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to retrieve withdrawals', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'Failed to retrieve packages', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({'error': 'Validation Error', 'details': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Failed to create package', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            purchase = serializer.save(user=request.user)  # Set the user here
            purchase.distribute_profit()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response({'error': 'Validation Error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Purchase failed', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(user=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to retrieve purchases', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)