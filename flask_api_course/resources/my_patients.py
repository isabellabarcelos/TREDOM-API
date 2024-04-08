from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import HealthProfessional, PatientProfessionalRelationModel
from flask.views import MethodView
from schemas import IdSchema
from db import db

blp = Blueprint("MyPatients", "my_patients", description="Operations on patients")

@blp.route("/my-patients")
class MyPatients(MethodView):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()

        professional = HealthProfessional.query.filter_by(user_id=current_user['user_id']).first()
        if professional:
            patients = PatientProfessionalRelationModel.query.filter_by(professional_id=professional.id).all()
            
            patients = [req.patient.user.to_dict() for req in PatientProfessionalRelationModel.query.filter_by(professional_id=professional.id).all()]
            return {patients}, 200 
        else:
            abort(403, message='Only professionals can see my patients')
    
    @jwt_required()
    @blp.arguments(IdSchema)
    def delete(self, request_data):
        current_user = get_jwt_identity()

        professional = HealthProfessional.query.filter_by(user_id=current_user['user_id']).first()
        if not professional:
            abort(403, message='Only professionals can remove patients')

        relation = PatientProfessionalRelationModel.query.filter_by(professional_id=professional.id, patient_id=request_data['id']).first()
        if not relation:
            abort(404, message='Patient not found or not associated with this professional')

        db.session.delete(relation)
        db.session.commit()

        return {'message': 'Patient removed successfully'}, 200
    

      