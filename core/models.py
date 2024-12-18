from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Permission,Group
from django.core.validators import RegexValidator
# import phonenumbers
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.exceptions import ValidationError


phone_regex = RegexValidator(
        regex=r'^\d{9,15}$', 
        message="Phone number must be between 9 and 15 digits."
    )


class Country_Codes(models.Model):
    country_name = models.CharField(max_length=100,unique=True)
    calling_code = models.CharField(max_length=10,unique=True)

    def __str__(self):
        return f"{self.country_name} ({self.calling_code})"
    
    class Meta:
        ordering = ['calling_code']

class UserManager(BaseUserManager):
    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError('Either email or phone number must be provided')

        # Normalize the email if provided
        if email:
            email = self.normalize_email(email)

        # Handle phone number validation if provided and not a superuser
        if phone_number and not extra_fields.get('is_superuser'):
            full_number = f"{extra_fields.get('country_code')}{phone_number}"
            try:
                parsed_number = phonenumbers.parse(full_number, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError("Invalid phone number.")
                phone_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.NumberParseException:
                raise ValidationError("Invalid phone number format.")

        # Create and return the user object
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
 
    def create_superuser(self, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if email is None:
            raise ValueError('Superuser must have an email address.')

        return self.create_user(email=email, phone_number=phone_number, password=password, **extra_fields)


class User(AbstractBaseUser):
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Office Staff'),
        ('librarian', 'Librarian'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')

    name = models.CharField(max_length=255, blank=True, null=True)
    joining_date = models.DateField(null=True,blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True,validators=[phone_regex], null=True, blank=True)
    country_code = models.ForeignKey('Country_Codes', on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    groups = models.ManyToManyField(
        Group,
        related_name='core_user_groups',  # Add a unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    # Override user_permissions field with a unique related_name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='app1_user_permissions'  
    )
    
    def __str__(self):
        return self.email if self.email else self.phone_number

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

# division model for students
class Division(models.Model):
    name = models.CharField(max_length=10)  
    class_name = models.CharField(max_length=50) 

    def __str__(self):
        return f"{self.class_name} - {self.name}"

# student model
class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ] 
    gender = models.CharField(max_length=1, choices=gender_choices)
    address = models.TextField()
    roll_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='students')
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['roll_number', 'division'], name='unique_roll_number_per_division')
        ]
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.roll_number} ({self.division})"
    
# library history model
class LibraryHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='library_histories')
    book_name = models.CharField(max_length=255)
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status_choices = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='borrowed')

    def __str__(self):
        return f"{self.book_name} - {self.student.first_name}"

# fees history model
class FeesHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_histories')
    fee_type = models.CharField(max_length=50)  # e.g., 'Tuition', 'Library', etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status_choices = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='unpaid')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fee_type} - {self.amount} - {self.student.first_name}"


# office staff model
class OfficeStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='office_staff')
    custom_id = models.CharField(max_length=10, unique=True, editable=False, blank=True)
    department = models.CharField(max_length=100)  # e.g., 'Accounts', 'HR', etc.
    position = models.CharField(max_length=100)  # e.g., 'Accountant', 'HR Manager', etc.
    joining_date = models.DateField()  # Date of joining the organization

    def __str__(self):
        return f"{self.user.name} ({self.position})"
    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate the custom ID format
            self.custom_id = f'OS{self.user.id}'  # Format: OS{id}

        super(OfficeStaff, self).save(*args, **kwargs)

    def __str__(self):
        return self.custom_id
    
  # librarian model 
class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian')
    custom_id = models.CharField(max_length=10, unique=True, editable=False, blank=True)
    library_section = models.CharField(max_length=100)  # e.g., 'Science', 'Literature', etc.
    joining_date = models.DateField()  # Date when the librarian was hired
    shifts = models.CharField(max_length=100)  # Working shifts, e.g., 'Morning', 'Evening'
    books_managed = models.PositiveIntegerField(default=0)  # Number of books managed by the librarian

    def __str__(self):
        return f"{self.user.name} ({self.library_section})"
    
    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate the custom ID format
            self.custom_id = f'LB{self.user.id}'  # Format: LB{id}

        super(Librarian, self).save(*args, **kwargs)


    def __str__(self):
        return self.custom_id 
    
# library review
class LibraryReview(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE) 
    book = models.CharField(max_length=255)  
    rating = models.PositiveSmallIntegerField(
        choices=[
            (1, '1 Star'),
            (2, '2 Stars'),
            (3, '3 Stars'),
            (4, '4 Stars'),
            (5, '5 Stars'),
        ]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    