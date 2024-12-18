from rest_framework import serializers
from .models import User, OfficeStaff, Librarian,Student,LibraryHistory, FeesHistory ,LibraryReview
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

# register serializer
class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'country_code', 'role', 'password', 'joining_date']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        role = validated_data.pop('role', 'staff')  # Default to 'staff'
        user = User.objects.create_user(**validated_data, role=role)

        # Additional logic for specific roles
        if role == 'staff':
            joining_date = validated_data.pop('joining_date', timezone.now().date())  # Use default current date if not provided
            OfficeStaff.objects.create(user=user, joining_date=joining_date)  # Add joining_date here
        elif role == 'librarian':
            joining_date = validated_data.pop('joining_date', timezone.now().date())  # Use default current date if not provided
            Librarian.objects.create(user=user, joining_date=joining_date)  # Add joining_date here
        
        return user

# login for admin
from rest_framework import serializers
from .models import User

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(_('Both email and password are required.'))

        # Authenticate the user
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError(_('Invalid email or password.'))

        attrs['user'] = user
        return attrs

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']  # Ensure you have the required fields for login

# user serializer for creating user lb,os by admin
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'phone_number', 'country_code', 'role', 'joining_date', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # Make password write-only
        }

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()
class OfficeStaffSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Use the custom User model
    email = serializers.EmailField(source="user.email", required=True)
    class Meta:
        model = OfficeStaff
        fields = ['user', 'department', 'position', 'joining_date']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        user_data['is_staff'] = True  # Ensure the created user is marked as staff
        user = User.objects.create(**user_data)

        if password:
            user.set_password(password)
            user.save()

        office_staff = OfficeStaff.objects.create(user=user, **validated_data)
        return office_staff


    def validate_custom_id(self, value):
        if not value:
            raise serializers.ValidationError("custom_id is required.")
        return value


class LibrarianSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Librarian
        fields = ['user', 'library_section', 'shifts','books_managed','joining_date']

    def create(self, validated_data):
        # Extract user data from validated data
        user_data = validated_data.pop('user')

        # Set the role for user as 'staff'
        user_data['role'] = 'librarian'

        # Handle password hashing if provided
        password = user_data.get('password')
        if password:
            user_data['password'] = make_password(password)  # Hash the password

        # Create and save the User instance
        user = User.objects.create(**user_data)

        library_section = validated_data.get('library_section')
        shifts = validated_data.get('shifts')
        books_managed = validated_data.get('books_managed')
        joining_date = validated_data.get('joining_date')

        # Create and save the OfficeStaff instance, using the extracted data
        librarian = Librarian.objects.create(user=user, library_section=library_section, shifts=shifts, books_managed=books_managed,joining_date=joining_date)

        return librarian
    
#  student serializer
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

# library history serializer
class LibraryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryHistory
        fields = '__all__'

#  fees history serializer
class FeesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeesHistory
        fields = '__all__'
        
#  library review serializer
class LibraryReviewSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = LibraryReview
        fields = ['id', 'student', 'book', 'rating', 'comment', 'created_at']

# users serializer for updation and deletion

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone_number', 'country_code', 'role', 'joining_date', 'is_active', 'is_superuser', 'is_staff', 'password']
        extra_kwargs = {
            'password': {'write_only': True},  # Password should be write-only
        }

    def update(self, instance, validated_data):
        # Handle password update (if included in the request)
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)  # Hash the password
        
        # Update the user instance with the provided validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance