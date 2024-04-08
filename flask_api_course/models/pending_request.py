from db import db

class PendingRequestModel(db.Model):
    __tablename__ = "pending_requests"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    sender = db.relationship('UserModel', foreign_keys=[sender_id])
    receiver = db.relationship('UserModel', foreign_keys=[receiver_id])