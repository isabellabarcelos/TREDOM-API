from flask.views import MethodView
from models import UserModel, Patient, PendingRequestModel, HealthProfessional, PatientProfessionalRelationModel
from flask_smorest import Blueprint, abort
from schemas import UserAndProfileSchema, SendRequestSchema, IdSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from flask import request
import re
import json
blp = Blueprint("Relation Request", "relation and requests", description="Operations on relation and requests")

@blp.route("/request")
class RequestResource(MethodView):
    @jwt_required()
    def post(self):
        request_data = request.json
        current_user = get_jwt_identity()

        if not re.match(r'^[\w\.-]+@[\w\.-]+(\.\w{2,})+$', request_data["email"]):
            abort(400, message="Invalid email format.")

        professional_user = HealthProfessional.query.filter_by(user_id=current_user).first()
        
        if not professional_user:
            abort(404, message='Professional not found')
        
        patient_user = UserModel.query.filter_by(email=request_data['email']).first()
        
        if not patient_user:
            abort(404, message='Patient not found.')
        
        patient = Patient.query.filter_by(user_id=patient_user.id).first()

        if patient:
            existing_request = PendingRequestModel.query.filter_by(sender_id=professional_user.id, receiver_id=patient_user.id).first()
            if existing_request:
                abort(400, message='Relationship already exists.')

            new_request = PendingRequestModel(sender_id=professional_user.id, receiver_id=patient_user.id)
            db.session.add(new_request)
            db.session.commit()
            return {'message': 'Success'}, 201
        else:
            abort(404, message='Patient not found.')

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        professional = HealthProfessional.query.filter_by(user_id=current_user).first()
        if professional:
            patient_ids = [req.receiver_id for req in PendingRequestModel.query.filter_by(sender_id=current_user).all()]
            patients = Patient.query.filter(Patient.user_id.in_(patient_ids)).all()
            print(patients)
            patients_info = [{"id": patient.id, "user_id": patient.user_id, "name": patient.name, "email": patient.email, "birthday": str(patient.birthday), "location": patient.location, "gender": patient.gender} for patient in patients]
            return {'patients': patients_info}, 200
        
        patient = Patient.query.filter_by(user_id=current_user).first()
        if patient:
            professional_ids = [req.sender_id for req in PendingRequestModel.query.filter_by(receiver_id=current_user).all()]
            professionals = HealthProfessional.query.filter(HealthProfessional.user_id.in_(professional_ids)).all()
            professionals_info = [{"id": prof.id, "name": prof.name, "email": prof.email,"specialization": prof.specialization, "location": prof.location, "medical_register": prof.medical_register} for prof in professionals]
            return {'professionals': professionals_info}, 200

    @jwt_required()
    def delete(self):
        request_data = request.json
        current_user = get_jwt_identity()

        professional_user = HealthProfessional.query.filter_by(user_id=current_user).first()
        if professional_user:
            pending_request = PendingRequestModel.query.filter_by(sender_id=professional_user.user_id, receiver_id=request_data['id']).first()
            if pending_request:
                db.session.delete(pending_request)
                db.session.commit()
                return {'message': 'Request deleted successfully'}, 200
            else:
                abort(404, message='Request not found')

        patient_user = Patient.query.filter_by(user_id=current_user).first()
        if patient_user:
            pending_request = PendingRequestModel.query.filter_by(receiver_id=patient_user.user_id, sender_id=request_data['id']).first()
            if pending_request:
                db.session.delete(pending_request)
                db.session.commit()
                return {'message': 'Request deleted successfully'}, 200
            else:
                abort(404, message='Request not found')

        abort(404, message='User not found or not authorized')


@blp.route("/relation")
class RelationResource(MethodView):
    @jwt_required()
    def post(self):
        request_data = request.json
        current_user = get_jwt_identity()
        
        patient = Patient.query.filter_by(user_id=current_user).first()
        if not patient:
            abort(403, message='User is not a patient')

        professional_id = request_data.get('professional_id')
        pending_request = PendingRequestModel.query.filter_by(sender_id=professional_id, receiver_id=current_user).first()
        if pending_request:
            new_relation = PatientProfessionalRelationModel(professional_id=professional_id, patient_id=current_user)
            db.session.add(new_relation)
            db.session.commit()

            db.session.delete(pending_request)
            db.session.commit()

            return {'message': 'Accepted Request'}, 200
        else:
            abort(404, message='Request does not exist ')

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        professional = HealthProfessional.query.filter_by(user_id=current_user).first()
        if professional:
            patient_ids = [req.professional_id for req in PatientProfessionalRelationModel.query.filter_by(professional_id=current_user).all()]
            patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
            patients_info = [{"id": patient.id, "user_id": patient.user_id, "name": patient.name, "email": patient.email, "birthday": str(patient.birthday), "location": patient.location, "gender": patient.gender} for patient in patients]
            return {'patients': patients_info}, 200
        
        patient = Patient.query.filter_by(user_id=current_user).first()
        if patient:
            professional_ids = [req.patient_id for req in PatientProfessionalRelationModel.query.filter_by(patient_id=current_user).all()]
            professionals = HealthProfessional.query.filter(HealthProfessional.id.in_(professional_ids)).all()
            professionals_info = [{"id": prof.id, "name": prof.name, "email": prof.email,"specialization": prof.specialization, "location": prof.location, "medical_register": prof.medical_register} for prof in professionals]
            return {'professionals': professionals_info}, 200
    

    @jwt_required()
    def delete(self):
        request_data = request.json
        current_user = get_jwt_identity()
        
        patient = Patient.query.filter_by(user_id=current_user).first()
        if patient:
            relation = PatientProfessionalRelationModel.query.filter_by(professional_id=request_data['id'], patient_id=current_user).first()

        else:
            relation = PatientProfessionalRelationModel.query.filter_by(professional_id=current_user, patient_id=request_data['id']).first()
        if not relation:
            abort(404, message='Relation does not exist')

        db.session.delete(relation)
        db.session.commit()

        return {'message': 'Relation removed successfully'}, 200