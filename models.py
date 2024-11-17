# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # type: ignore

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50))  # "admin", "professional", "customer"
    name = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.Integer)
    address = db.Column(db.String(150))
    pincode = db.Column(db.Integer)
    experience = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

    # Relationship for service requests where the user is the customer
    customer_requests = db.relationship(
        'ServiceRequest', foreign_keys='ServiceRequest.customer_id', 
        back_populates='customer', lazy=True
    )
    # Relationship for service requests where the user is the professional
    professional_requests = db.relationship(
        'ServiceRequest', foreign_keys='ServiceRequest.professional_id', 
        back_populates='professional', lazy=True
    )
    # servicee=db.relationship('Service', foreign_keys='Service.id', back_populates='customerr', lazy=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_of_request = db.Column(db.DateTime)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(50))  # e.g., "requested", "assigned", "closed"
    remarks = db.Column(db.Text)

    # Relationship with Service
    service = db.relationship('Service', back_populates='service_requests', lazy=True)
    # Relationship with User (customer)
    customer = db.relationship('User', foreign_keys=[customer_id], back_populates='customer_requests', lazy=True)
    # Relationship with User (professional)
    professional = db.relationship('User', foreign_keys=[professional_id], back_populates='professional_requests', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    proname = db.Column(db.String(100), nullable=False)
    prophone = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer)
    description = db.Column(db.Text)
    
    # Relationship for service requests
    service_requests = db.relationship('ServiceRequest', back_populates='service', lazy=True)
    # customerr=db.relationship('User', back_populates='servicee', lazy=True)