# import os
# import redis
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from models import UserModel, Patient, HealthProfessional
from schemas import PatientSchema, HealthProfessionalSchema, UserAndProfileSchema, UserSchema
# from rq import Queue

# from tasks import send_user_registration_email

from db import db
from models import UserModel
from schemas import UserSchema, UserRegisterSchema
from blocklist import BLOCKLIST

blp = Blueprint("Users", "users", description="Operations on users")
# connection = redis.from_url(
#     os.getenv("REDIS_URL")
# )  # Get this from Render.com or run in Docker
# queue = Queue("emails", connection=connection)


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserAndProfileSchema)
    def post(self, user_data):
        profile_type = user_data.get("profile_type")

        if profile_type not in ["patient", "professional"]:
            abort(400, message="Invalid profile type. It should be 'patient' or 'professional'.")

        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="A user with that email already exists.")

        password_hash = pbkdf2_sha256.hash(user_data["password"])

        try:
            user = UserModel(email=user_data["email"], password=password_hash)
            db.session.add(user)
            db.session.commit()
            print(user_data)
            if profile_type == "patient":
                patient = Patient(
                    user_id=user.id,
                    name=user_data["patient"]["name"],
                    birthday=user_data["patient"]["birthday"],
                    location=user_data["patient"]["location"],
                    gender=user_data["patient"]["gender"],
                    weight=user_data["patient"]["weight"],
                    race=user_data["patient"]["race"],
                    height=user_data["patient"]["height"]
                )
                db.session.add(patient)
            else:
                health_professional = HealthProfessional(
                    user_id=user.id,
                    name=user_data["patient"]["name"],
                    birthday=user_data["patient"]["birthday"],
                    location=user_data["patient"]["location"],
                    gender=user_data["patient"]["gender"],
                    medical_register=user_data["patient"]["medical_register"]
                )
                db.session.add(health_professional)

            db.session.commit()

            return {"message": "User created successfully."}, 201

        except IntegrityError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the user.")




@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.email == user_data["email"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserAndProfileSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @blp.arguments(UserAndProfileSchema)
    def put(self, user_data, user_id):
        user = UserModel.query.get_or_404(user_id)
        # Atualizar os dados do usuário com os dados fornecidos na requisição
        user.email = user_data.get('email', user.email)
        user.password = user_data.get('password', user.password)

        # Se o perfil do usuário for "patient", atualize os dados do paciente
        if Patient.query.filter_by(user_id=user_id).first():
            patient_data = user_data.get('patient', {})
            patient = Patient.query.filter_by(user_id=user_id).first()
            if patient:
                patient.name = patient_data.get('name', patient.name)
                patient.birthday = patient_data.get('birthday', patient.birthday)
                patient.location = patient_data.get('location', patient.location)
                patient.gender = patient_data.get('gender', patient.gender)
                patient.weight = patient_data.get('weight', patient.weight)
                patient.race = patient_data.get('race', patient.race)
                patient.height = patient_data.get('height', patient.height)

        # Se o perfil do usuário for "health_professional", atualize os dados do profissional de saúde
        elif HealthProfessional.query.filter_by(user_id=user_id).first():
            health_professional_data = user_data.get('health_professional', {})
            health_professional = HealthProfessional.query.filter_by(user_id=user_id).first()
            if health_professional:
                health_professional.name = health_professional_data.get('name', health_professional.name)
                health_professional.birthday = health_professional_data.get('birthday', health_professional.birthday)
                health_professional.location = health_professional_data.get('location', health_professional.location)
                health_professional.gender = health_professional_data.get('gender', health_professional.gender)
                health_professional.medical_register = health_professional_data.get('medical_register', health_professional.medical_register)

        # Confirmar as alterações no banco de dados
        db.session.commit()

        return {"message": "User updated successfully."}, 200
    
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        
        patient = Patient.query.filter_by(user_id=user_id).first()
        if patient:
            db.session.delete(patient)
        
        health_professional = HealthProfessional.query.filter_by(user_id=user_id).first()
        if health_professional:
            db.session.delete(health_professional)
        
        db.session.delete(user)
        db.session.commit()
        
        return {"message": "User and related data deleted."}, 200

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200