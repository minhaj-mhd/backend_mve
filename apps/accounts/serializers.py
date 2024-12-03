from rest_framework import serializers
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from .models import User, BusinessProfile, CustomerProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(validators=[validate_email])
    newsletter_subscription = serializers.BooleanField(required=False, default=False)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 
                 'newsletter_subscription', 'date_of_birth']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
        }

    def create(self, validated_data):
        newsletter_subscription = validated_data.pop('newsletter_subscription', False)
        date_of_birth = validated_data.pop('date_of_birth', None)

        user = User.objects.create_user(
            username=validated_data['email'],
            is_customer=True,
            is_business=False,
            **validated_data
        )

        CustomerProfile.objects.create(
            user=user,
            newsletter_subscription=newsletter_subscription,
            date_of_birth=date_of_birth
        )

        return user

class BusinessRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(validators=[validate_email])
    business_email = serializers.EmailField(validators=[validate_email])
    business_name = serializers.CharField(required=True)
    business_address = serializers.CharField(required=True)
    business_registration_number = serializers.CharField(required=True)
    business_phone = serializers.CharField(required=False)
    business_description = serializers.CharField(required=False)
    tax_id = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number',
                 'business_name', 'business_email', 'business_phone', 'business_address',
                 'business_description', 'business_registration_number', 'tax_id']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
        }

    def create(self, validated_data):
        business_data = {
            'business_name': validated_data.pop('business_name'),
            'business_email': validated_data.pop('business_email'),
            'business_phone': validated_data.pop('business_phone', ''),
            'business_address': validated_data.pop('business_address'),
            'business_description': validated_data.pop('business_description', ''),
            'business_registration_number': validated_data.pop('business_registration_number'),
            'tax_id': validated_data.pop('tax_id', '')
        }

        user = User.objects.create_user(
            username=validated_data['email'],
            is_customer=False,
            is_business=True,
            **validated_data
        )

        BusinessProfile.objects.create(
            user=user,
            **business_data
        )

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[validate_email])
    password = serializers.CharField()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom claims or modify the response data
        data['user_type'] = 'business' if self.user.is_business else 'customer'
        return data
