from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

from .models import User, BusinessProfile, CustomerProfile

@api_view(['POST'])
@permission_classes([AllowAny])
def register_customer(request):
    try:
        with transaction.atomic():
            data = request.data
            
            # Validate email
            validate_email(data['email'])
            
            # Validate password
            validate_password(data['password'])
            
            # Create user
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone_number=data.get('phone_number', ''),
                is_customer=True,
                is_business=False
            )
            
            # Create customer profile
            CustomerProfile.objects.create(
                user=user,
                newsletter_subscription=data.get('newsletter_subscription', False),
                date_of_birth=data.get('date_of_birth', None)
            )
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'Customer account created successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
            
    except ValidationError as e:
        return Response({
            'status': 'error',
            'message': e.messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_business(request):
    try:
        with transaction.atomic():
            data = request.data
            
            # Validate email
            validate_email(data['email'])
            validate_email(data['business_email'])
            
            # Validate password
            validate_password(data['password'])
            
            # Create user
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone_number=data.get('phone_number', ''),
                is_customer=False,
                is_business=True
            )
            
            # Create business profile
            business_profile = BusinessProfile.objects.create(
                user=user,
                business_name=data['business_name'],
                business_email=data['business_email'],
                business_phone=data.get('business_phone', ''),
                business_address=data['business_address'],
                business_description=data.get('business_description', ''),
                business_registration_number=data['business_registration_number'],
                tax_id=data.get('tax_id', '')
            )
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'Business account created successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
            
    except ValidationError as e:
        return Response({
            'status': 'error',
            'message': e.messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user_type'] = 'business' if user.is_business else 'customer'
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validate email
        validate_email(email)
        
        user = authenticate(username=email, password=password)
        
        if user is None:
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'user_type': 'business' if user.is_business else 'customer',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
        
    except ValidationError as e:
        return Response({
            'status': 'error',
            'message': e.messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

