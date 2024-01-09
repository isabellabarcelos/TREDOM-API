from rest_framework import serializers
from .models import User
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'profileType')

from datetime import date

class PatientSerializer(UserSerializer):
    # Campos do serializador
    fullName = serializers.CharField(max_length=200)
    date = serializers.DateField()
    phone = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=20)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('fullName', 'date', 'phone', 'city', 'gender')

    def validate(self, data):
        # Campos obrigatórios
        required_fields = ['fullName', 'date', 'phone', 'city', 'gender']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"All fields are required.")

        # Validando 'fullName', 'city', 'gender' para conter apenas letras
        for field in ['fullName', 'city', 'gender']:
            if not data[field].replace(' ', '').isalpha():
                raise serializers.ValidationError(f"{field} must contain only letters.")

            # Capitalizando a primeira letra de cada palavra no campo
            data[field] = ' '.join(word.capitalize() for word in data[field].split())

        # Verificando se a data fornecida não é maior que a data atual
        provided_date = data.get('date')
        if provided_date and provided_date > date.today():
            raise serializers.ValidationError("The provided date cannot be in the future.")
        
        if provided_date:
            data['date'] = provided_date.strftime('%d/%m/%Y') 
        
        # Verificando se o campo 'phone' contém apenas números
        if not data['phone'].isdigit():
            raise serializers.ValidationError("Phone must contain only digits.")


        return data


class ProfessionalSerializer(UserSerializer):
    # Campos do serializador
    fullName = serializers.CharField(max_length=200)
    date = serializers.DateField()
    city = serializers.CharField(max_length=100)
    medicalregister = serializers.CharField(max_length=100)
    medicalspecialty = serializers.CharField(max_length=100)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('fullName', 'date', 'city', 'medicalregister', 'medicalspecialty')

    def validate(self, data):
        # Campos obrigatórios
        required_fields = ['fullName', 'date', 'city', 'medicalregister', 'medicalspecialty']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"All fields are required.")

        # Validando 'fullName', 'city', 'medicalregister', 'medicalspecialty' para conter apenas letras
        for field in ['fullName', 'city', 'medicalregister', 'medicalspecialty']:
            if not data[field].replace(' ', '').isalpha():
                raise serializers.ValidationError(f"{field} must contain only letters.")

            # Capitalizando a primeira letra de cada palavra no campo
            data[field] = ' '.join(word.capitalize() for word in data[field].split())

        # Verificando se a data fornecida não é maior que a data atual
        provided_date = data.get('date')
        if provided_date and provided_date > date.today():
            raise serializers.ValidationError("The provided date cannot be in the future.")

        return data

