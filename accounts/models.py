from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_health_professional = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    birthday = models.DateField()
    location = models.CharField(max_length=255)
    gender = models.CharField(max_length=20)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    race = models.CharField(max_length=20)
    height = models.DecimalField(max_digits=5, decimal_places=2)

class HealthProfessional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    birthday = models.DateField()
    location = models.CharField(max_length=255)
    gender = models.CharField(max_length=20)
    medical_register = models.CharField(max_length=20)

class PatientHealthProfessionalRelationship(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    health_professional = models.ForeignKey(HealthProfessional, on_delete=models.CASCADE)
    can_configure_device = models.BooleanField(default=True)
