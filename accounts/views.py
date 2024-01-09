import re  # Importando o módulo de expressões regulares
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt, datetime
from rest_framework import status


# Create your views here.

from rest_framework import serializers
from .models import User  # Assuming you have a User model
    
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Patient, Professional
from .serializers import UserSerializer, ProfessionalSerializer, PatientSerializer
from django.contrib.auth.hashers import make_password

class FinalizeRegistrationView(APIView):
    def post(self, request):
         
        if request.data['profileType'] == 'Paciente':
            serializer = PatientSerializer(data=request.data)
        elif request.data['profileType'] == 'Profissional da Saúde':
            serializer = ProfessionalSerializer(data=request.data)

        if serializer.is_valid():
            user_data = serializer.validated_data
            profile_type = user_data.get('profileType')
            
            # Salvando o usuário
            user = User.objects.create(
                email=user_data['email'],
                password= make_password(user_data['password']),
                profileType=profile_type
            )
            
            # Lógica para salvar informações adicionais com base no tipo de perfil
            if profile_type == 'Paciente':
                Patient.objects.create(
                    user=user,
                    fullName=user_data.get('fullName'),
                    date=user_data.get('date'),
                    city=user_data.get('city'),
                    phone=user_data.get('phone'),
                    gender=user_data.get('gender')
                )
            elif profile_type == 'Profissional da Saúde':
                Professional.objects.create(
                    user=user,
                    fullName=user_data.get('fullName'),
                    date=user_data.get('date'),
                    city=user_data.get('city'),
                    medicalregister=user_data.get('medicalregister'),
                    medicalspecialty=user_data.get('medicalspecialty')
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = serializer.errors
            if errors:
                first_error_field, first_error_message = next(iter(errors.items()))
                error_message = f"{first_error_field}: {first_error_message[0]}"
            
            return Response({"message": error_message}, status=status.HTTP_400_BAD_REQUEST)




class FirstStepRegistrationView(APIView):
    def post(self, request):
        # Retrieving data from the POST request
        profile_type = request.data.get('profileType')
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirmPassword')
        full_name = request.data.get('fullName')

        # Fields validation
        if not (profile_type and email and password and confirm_password and full_name):
            return Response({'message': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({'message': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        # Password validation: at least 8 characters, 1 uppercase letter, and 1 digit
        if not (len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password)):
            return Response({'message': 'Password must contain at least 8 characters, 1 uppercase letter, and 1 digit.'}, status=status.HTTP_400_BAD_REQUEST)

        # Email format validation using regex
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return Response({'message': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)
      
        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Name validation: only letters
        if not full_name.replace(' ', '').isalpha():
            return Response({'message': 'Name must contain only letters.'}, status=status.HTTP_400_BAD_REQUEST)

        # If all fields are correct, proceed to the next step
        # You can redirect to the next route or return a status indicating that the first step was successfully completed
        return Response({'message': 'First step completed successfully. Next step: Finalize Registration.'}, status=status.HTTP_200_OK)



class LoginView(APIView):
    def post(self, request):
      email = request.data['email']
      password = request.data['password']

      user = User.objects.filter(email=email).first()

      if (user is None) or (not user.check_password(password)):
        return Response({'message': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)
      
      payload = {
         'id': user.id,
          'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
          'iat': datetime.datetime.utcnow()
      }

      token = jwt.encode(payload, 'secret', algorithm='HS256')

      response = Response()
      response.set_cookie(key='jwt', value=token, httponly=True)
      response.data = {
         'jwt': token
      }
      
      return response
    
class UserView(APIView):
    def get(self, request):
      token = request = request.COOKIES.get('jwt')

      if not token:
         raise AuthenticationFailed('Unauthenticated!')
      
      try:
         payload = jwt.decode(token, 'secret', algorithms=['HS256'])
      except jwt.ExpiredSignatureError:
         raise AuthenticationFailed('Unauthenticated!')
    
      user =  User.objects.filter(id=payload['id']).first()
      serializer = UserSerializer(user)

      return Response(serializer.data)
    

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
        'message': 'success'
        }

        return response
  