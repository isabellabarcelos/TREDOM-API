from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt, datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import User, Patient, HealthProfessional
from .serializers import UserSerializer, PatientSerializer, HealthProfessionalSerializer

# Create your views here.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import PatientSerializer, HealthProfessionalSerializer

class RegisterView(APIView):
   def post(self, request):
      user_data = {
            'name': request.data.get('name', ''),
            'email': request.data.get('email', ''),
            'password': request.data.get('password', ''),
      }

      is_patient = request.data.get('is_patient', False)
      is_health_professional = request.data.get('is_health_professional', False)

      if is_patient and is_health_professional:
         return Response({'message': 'Choose only one type of user: patient or health professional.'}, status=status.HTTP_400_BAD_REQUEST)

      if not is_patient and not is_health_professional:
         return Response({'message': 'Specify the user type: patient or health professional.'}, status=status.HTTP_400_BAD_REQUEST)

      user_serializer = UserSerializer(data=user_data)

      if user_serializer.is_valid():
         user = user_serializer.save()
         if is_patient:  
            patient_data = {
               'name': request.data.get('name', ''),
               'email': request.data.get('email', ''),
               'birthday': request.data.get('birthday', ''),
               'location': request.data.get('location', ''),
               'gender': request.data.get('gender', ''),
               'weight': request.data.get('weight', ''),
               'race': request.data.get('race', ''),
               'height': request.data.get('height', '')
            }
            patient_data['user'] = user.id
            patient_serializer = PatientSerializer(data=patient_data)
            if patient_serializer.is_valid():
               patient_serializer.save()
               return Response({'message': 'Patient registered successfully'}, status=status.HTTP_201_CREATED)
            else:
               user.delete()
               return Response(patient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         elif is_health_professional:
               professional_data = {
                  'name': request.data.get('name', ''),
                  'email': request.data.get('email', ''),
                  'birthday': request.data.get('birthday', ''),
                  'location': request.data.get('location', ''),
                  'gender': request.data.get('gender', ''),
                  'medical_register': request.data.get('medical_register', '')
               }

               professional_data['user'] = user.id
               professional_serializer = HealthProfessionalSerializer(data=professional_data)
               if professional_serializer.is_valid():
                  professional_serializer.save()
                  return Response({'message': 'Health professional registered successfully'}, status=status.HTTP_201_CREATED)
               else:
                  user.delete()
                  return Response(professional_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
      email = request.data['email']
      password = request.data['password']

      user = User.objects.filter(email=email).first()

      if user is None:
         raise AuthenticationFailed('User not found!')
      
      if not user.check_password(password):
         raise AuthenticationFailed('Incorrect password!')
      
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
  