from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    PROFILE_CHOICES = (
        ('Paciente', 'Paciente'),
        ('Profissional da Saúde', 'Profissional da Saúde'),
    )

    email = models.EmailField(max_length=150, unique=True)
    username = None
    password = models.CharField(max_length=255)
    profileType = models.CharField(max_length=50, choices=PROFILE_CHOICES, default='N')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['profileType','password']

    def __str__(self):
        return self.email

class Professional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    fullName = models.CharField(max_length=255, default='N')
    date = models.DateField()
    city = models.CharField(max_length=100)
    medicalregister = models.CharField(max_length=100)
    medicalspecialty = models.CharField(max_length=100)
    patients = models.ManyToManyField('Patient', related_name='associated_professionals')
    
    def __str__(self):
        return f"Professional: {self.fullName}"
    

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    fullName = models.CharField(max_length=255, default='NA')
    date = models.DateField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    professionals = models.ManyToManyField('Professional', related_name='associated_patients')
    
    def __str__(self):
        return f"Patient: {self.fullName}"

