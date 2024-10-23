from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timezone,timedelta



metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)


class User(db.Model,SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False,default='customer')  # (customers,admin or customer service)
    
    # Relationships
    sent_parcels = db.relationship('Parcel', foreign_keys='Parcel.sender_id', back_populates='sender')
    received_parcels = db.relationship('Parcel', foreign_keys='Parcel.recipient_id', back_populates='recipient')
    
    #this is the relationship between customer service and the parcel 
    parcels = db.relationship('UserParcelAssignment', back_populates='user', cascade='all, delete-orphan')
    
    serialize_rules = ('-sent_parcels', '-received_parcels', '-parcels')    
    

    
    def __repr__(self):
        return f'<User {self.name}, Role: {self.role}>'
    
    def set_password(self,password):
        self.password=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password,password)
    
    @classmethod
    def get_user_by_name(cls,name):
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_user_by_phone(cls,phone_number):
        return cls.query.filter_by(phone_number=phone_number).first()
    
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Parcel(db.Model,SerializerMixin):
    __tablename__ = 'parcels'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    tracking_number = db.Column(db.String, unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False, default='Pending')  # (pending,in_transit,delivered)
    shipping_cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))

    #FOREIGN IDS
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    location_id=db.Column(db.Integer,db.ForeignKey('locations.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_parcels')
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='received_parcels')
    vehicle = db.relationship('Vehicle', back_populates='parcels')
    location=db.relationship('Location',back_populates='parcels')
    customer_service_assignments = db.relationship('UserParcelAssignment', back_populates='parcel', cascade='all, delete-orphan')
    
    serialize_rules = ('-customer_service_assignments', '-vehicle', '-location')
    
   

    
    def __repr__(self):
        return f'<Parcel {self.tracking_number}, {self.status}, Cost: {self.shipping_cost}>'


class Vehicle(db.Model,SerializerMixin):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String, unique=True, nullable=False)
    capacity=db.Column(db.Float ,nullable=False)
    driver_name = db.Column(db.String, nullable=False)
    driver_phone = db.Column(db.String, nullable=False)
    departure_time=db.Column(db.String)
    expected_arrival_time=db.Column(db.String)
    status=db.Column(db.String ,default='empty')
    
    #Foreign id
    location_id=db.Column(db.Integer,db.ForeignKey('locations.id'))
    
    #Relationships
    parcels = db.relationship('Parcel', back_populates='vehicle')
    location=db.relationship('Location',back_populates='vehicles')
    
    serialize_rules = ('-location',)
    

    def __repr__(self):
        return f'<Vehicle {self.number_plate}, Driver: {self.driver_name}>'

# we have used this table for calculating the rates this table is only used by the admin who sets different rates
class Location(db.Model,SerializerMixin):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    cost_per_kg = db.Column(db.Float, nullable=False)
    
    #Relationships
    parcels=db.relationship('Parcel',back_populates='location')
    vehicles=db.relationship(Vehicle,back_populates='location')
    
    serialize_rules = ('-parcels',)
    
    
    
    

    def __repr__(self):
        return f'<Location {self.origin} to {self.destination}, Cost: {self.cost_per_kg} per kg>'


class UserParcelAssignment(db.Model,SerializerMixin):
    __tablename__ = 'user_parcel_assignments'
    id = db.Column(db.Integer, primary_key=True)
    
    #FOREIGN ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) #this is a customer service/admin user
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'))

    #RELATIONSHIPS
    user = db.relationship('User', back_populates='parcels')
    parcel = db.relationship('Parcel', back_populates='customer_service_assignments')
    serialize_rules = ('-user.parcels', '-parcel.customer_service_assignments')
    
    

    def __repr__(self):
        return f'<UserParcelAssignment User: {self.user_id}, Parcel: {self.parcel_id}>'


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)