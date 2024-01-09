from rest_framework import serializers
from .models import User, Patient, Professional

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'profileType')

class PatientSerializer(UserSerializer):
    fullName = serializers.CharField(max_length=200)
    date = serializers.DateField()
    phone = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=20)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('fullName','date', 'phone', 'city', 'gender')

    def validate(self, data):
        required_fields = ['fullName', 'date', 'phone', 'city', 'gender']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required for Patient profile type.")
        return data

class ProfessionalSerializer(UserSerializer):
    fullName = serializers.CharField(max_length=200)
    date = serializers.DateField()
    city = serializers.CharField(max_length=100)
    medicalregister = serializers.CharField(max_length=100)
    medicalspecialty = serializers.CharField(max_length=100)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('fullName','date', 'city', 'medicalregister', 'medicalspecialty')

    def validate(self, data):
        required_fields = ['fullName', 'date', 'city', 'medicalregister', 'medicalspecialty']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required for Professional profile type.")
        return data
