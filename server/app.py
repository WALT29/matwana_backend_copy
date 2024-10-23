from models import db,User,Parcel,Vehicle,Location,UserParcelAssignment
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from flask_cors import CORS
from auth import auth_bp,jwt,allow
from datetime import timedelta
import os 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app=Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']='e173db52f146f6d5e957a922'
app.config['JWT_ACCESS_TOKEN_EXPIRES']=timedelta(hours=2)
app.config['JWT_REFRESH_TOKEN_EXPIRES']=timedelta(days=3)
app.register_blueprint(auth_bp)
app.json.compact = False

db.init_app(app)
jwt.init_app(app)
api=Api(app)


@app.route('/')
def index():
    return '<h1>Matwana Logistics</h1>'

###################################################USER RESOURCE###################################################################

class Users(Resource):
    @jwt_required()
    @allow(['admin','customer_service'])
    def get(self):
        users=[]
        for user in User.query.all():
            response_body={
                "id":user.id,
                "name":user.name,
                "phone_number":user.phone_number,
                "email":user.email,
                "role":user.role
            }
            users.append(response_body)
        
        return make_response(users,200)

        
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def post(self):
        data=request.get_json()
        name=data['name']
        phone_number=data['phone_number']
        email=data['email']
        password=data['password']
        role=data['role']
        
        errors=[]
        if len(name)<2:
            errors.append("Name is required and name should be at least 3 characters")
        if not phone_number.isdigit() or not len(phone_number) ==10:
            errors.append('Phone number should be 10 characters and have digits only')
        if not "@" in email or not email:
            errors.append('email is required')
        if len(password) <8 :
            errors.append('Password should be at least 8 characters')
        
        user =User.get_user_by_name(name=name)
        
        if user is not None:
            errors.append("User with that username exists")
        
        if errors:
            return make_response({
                "errors":errors
            },400)
            
        new_user=User(name=name,
                      phone_number=phone_number,
                      email=email,
                      role=role)
        
        new_user.set_password(password=password)
        new_user.save()
        
        return make_response({
            "name":name,
            "phone_number":phone_number,
            "password":password
        },201)
        
api.add_resource(Users,'/users')

class User_by_id(Resource):
    @jwt_required()
    @allow(['admin','customer_service'])
    def get(self,id):
        user=User.query.filter_by(id=id).first()
        if not user:
            return make_response({
                "error":"No user found"
            },400)
        return make_response(user.to_dict(),200)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def delete(self,id):
        user=User.query.filter_by(id=id).first()
        if not user:
            return make_response({
                "error":"No user found"
            },400)
        
        
        user.delete()
        
        return make_response({
            "message":"user delete successfully"
        },200)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def put(self,id):
        user=User.query.filter_by(id=id).first()
        if not user:
            return make_response({
                "error":"User not found"
            })
        
        data=request.get_json()
        for key,value in data.items():
            setattr(user,key,value)
        db.session.commit()
        
        return make_response(user.to_dict(),200)
api.add_resource(User_by_id,'/users/<int:id>')


############################################## PARCEL RESOURCE ###################################################################
class Parcels(Resource):
    @jwt_required()
    @allow(['admin','customer_service','customer'])
    def get(self):
        parcels=[parcel.to_dict() for parcel in Parcel.query.all()]
        return make_response(parcels,200)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def post(self):
        data=request.get_json()
        user_id=data['user_id']
        name=data['name']
        description=data['description']
        tracking_number=data['tracking_number']
        weight=data['weight']
        status=data['status']
        sender_id = data['sender_id']  
        recipient_id = data['recipient_id']
        location_id=data['location_id']  
        vehicle_id = data['vehicle_id']  
        
        user=User.query.filter_by(id=user_id).first()
        sender=User.query.filter_by(id=sender_id).first()
        recipient=User.query.filter_by(id=recipient_id).first()
        vehicle=Vehicle.query.filter_by(id=vehicle_id).first()
        location=Location.query.filter_by(id=location_id).first()
         
        if not user or user.role not in ['customer_service','admin']:
            return make_response({
                "error":"Invalid user Id or insufficient permission"
            },403)
        
        if not sender or not recipient or not location:
            return make_response({
                "error":"Please enter a valid sender,recipient,vehicle or location details"
            },400)
            
        
        if not description or not weight or not name:
            return make_response({
                "errors":"please enter  all parcel information"
            },400)
        
        shipping_cost=location.cost_per_kg*weight
       
        parcel=Parcel(
            name=name,
            description=description,
            tracking_number=tracking_number,
            weight=weight,
            status=status,
            shipping_cost=shipping_cost,
            sender_id = sender_id,  
            recipient_id = recipient_id,
            location_id=location_id, 
            vehicle_id = vehicle_id  
            )
        user_parcel_assignment=UserParcelAssignment(user=user,parcel=parcel)
        db.session.add(user_parcel_assignment)
        db.session.add(parcel)
        db.session.commit()
        
        parcel_dict={
            "name":parcel.name,
            "description":parcel.description,
            "tracking_number":parcel.tracking_number,
            "weight":parcel.weight,
            "status":parcel.status,
            "shipping_cost":parcel.shipping_cost,
            "sender_id":parcel.sender_id,  
            "recipient_id":parcel.recipient_id,
            "location_id":parcel.location_id, 
            "vehicle_id":parcel.vehicle_id  
        }
        
        return make_response(parcel_dict,201)

api.add_resource(Parcels,'/parcels')

class Parcel_by_id(Resource):
    @jwt_required()
    @allow(['admin','customer_service','customer'])
    def get(self,id):
        parcel=Parcel.query.filter_by(id=id).first()
        
        if not parcel:
            return make_response({
                "error":"Parcel not found"
            },400)
        
        return make_response(parcel.to_dict(),200)
    
    @jwt_required()
    @allow(['admin','customer_service','customer'])
    def delete(self,id):
        parcel=Parcel.query.filter_by(id=id).first()
        if not parcel:
            return make_response({
                "error":"Parcel not found"
            },400)
        
        db.session.delete(parcel)
        db.session.commit()
        return make_response({
            "message":"parcel successfully deleted"
        },200)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def put(self,id):
        parcel=Parcel.query.filter_by(id=id).first()
        data=request.get_json()
        if not parcel:
            return make_response({
                "error":"Parcel not found"
            },400)
        
        
        for key,value in data.items():
            setattr(parcel,key,value)
        
        db.session.commit()
        
        return make_response(parcel.to_dict(),200)

api.add_resource(Parcel_by_id,'/parcels/<int:id>')

################################################## VEHICLES RESOURCE ######################################

class Vehicles(Resource):
    def get(self):
        vehicles=[vehicle.to_dict() for vehicle in Vehicle.query.all()]
        if not vehicles:
            return make_response({
                "message":"no vehicles found"
            },200)
        return make_response(vehicles,200)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def post(self):
        data=request.get_json()
        number_plate=data['number_plate']
        capacity=data['capacity']
        driver_name=data['driver_name']
        driver_phone=data['driver_phone']
        departure_time=data['departure_time']
        expected_arrival_time=data['expected_arrival_time']
        status=data['status']
        location_id=data['location_id']
        
        location=Location.query.filter_by(id=location_id).first()
        
        if not location:
            return make_response({
                "error":"Please enter a valid location"
            },400)
        
        if not number_plate or not capacity:
            return make_response({
                "error":"Please insert the number plate details of the vehicle"
            },400)
        
        vehicle=Vehicle(number_plate=number_plate,
                        capacity=capacity,
                        driver_name=driver_name,
                        departure_time=departure_time,
                        expected_arrival_time=expected_arrival_time,
                        driver_phone=driver_phone,
                        status=status,
                        location_id=location_id
                        )
        db.session.add(vehicle)
        db.session.commit()
        
        return make_response(vehicle.to_dict(),200)

api.add_resource(Vehicles,'/vehicles')


class Vehicle_by_id(Resource):
    @jwt_required()
    @allow(['admin','customer_service'])
    def get(self,id):
        vehicle=Vehicle.query.filter_by(id=id).first()
        
        if not vehicle:
            return make_response({
                "error":"No vehicle found"
            },400)
        return make_response(vehicle.to_dict(),200)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def delete(self,id):
        vehicle=Vehicle.query.filter_by(id=id).first()
        if not vehicle:
            return make_response({
                "error":"No vehicle found"
            },400)
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return make_response({
            "message":"vehicle deleted"
        },204)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def put(self,id):
        vehicle=Vehicle.query.filter_by(id=id).first()
        data=request.get_json()
        if not vehicle:
            return make_response({
                "error":"No vehicle found"
            },400)
        
        for key,value in data.items():
            setattr(vehicle,key,value)
        
        db.session.commit()
        
        return make_response(vehicle.to_dict(),200)

api.add_resource(Vehicle_by_id,'/vehicles/<int:id>')

################################################### LOCATION RESOURCE ############################################################

class Locations(Resource):
    def get(self):
        locations=[location.to_dict() for location in Location.query.all()]
        
        if  not locations:
            return make_response({
                "error":"No location is found"
            },400)
        
        return make_response(locations,200)
    
    @jwt_required()
    @allow(['admin'])
    def post(self):
        data=request.get_json()
        origin=data['origin']
        destination=data['destination']
        cost_per_kg=data['cost_per_kg']
        
        if not origin or not destination or not cost_per_kg:
            return make_response({
                "error":"please enter all the details the origin ,destination and cost_per_kg"
            },400)
        
        location=Location(origin=origin,destination=destination,cost_per_kg=cost_per_kg)
        db.session.add(location)
        db.session.commit()
        
        return make_response(location.to_dict(),200)
    
    @jwt_required()
    @allow(['admin'])
    def delete(self):
        locations=[location.to_dict() for location in Location.query.all()]
        
        if  not locations:
            return make_response({
                "error":"No location is found"
            },400)
        
        Location.query.delete()
        
        return make_response({
            "message":"All Locations  have been deleted"
        },200)
        
api.add_resource(Locations,'/locations')

class Locations_by_id(Resource):
    @jwt_required()
    @allow(['admin','customer_service'])
    def get(self,id):
        location=Location.query.filter_by(id=id).first()
        
        if not location:
            return make_response({
                "error":"No location is found"
            },400)
            
        return make_response(location.to_dict(),200)
    
    @jwt_required()
    @allow(['admin'])
    def delete(self,id):
        location=Location.query.filter_by(id=id).first()
        if not location:
            return make_response({
                "error":"No location is found"
            },400)
        
        db.session.delete(location)
        db.session.commit()
        
        return make_response({
            "body":"Location is deleted"
        },204)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def put(self,id):
        location=Location.query.filter_by(id=id).first()
        data=request.get_json()
        if not location:
            return make_response({
                "error":"No location is found"
            },400)
        
        for key,value in data.items():
            setattr(location,key,value)
        
        db.session.commit()
        return make_response(location.to_dict(),200)

api.add_resource(Locations_by_id,'/locations/<int:id>')

################################################# CUSTOMER SERVICE RESOURCE ######################################################
class Userparcels(Resource):
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def get(self,id):
        user=User.query.filter_by(id=id).first()
        
        if not user or user.role not in ['customer_service','admin']:
            return make_response({"error": "Invalid user ID or Insufficient user role"}, 400)
        
        assignments=UserParcelAssignment.query.filter_by(user_id=id).all()
        parcels=[assignment.parcel.to_dict() for assignment in assignments]
        
        return make_response(parcels,200)
    
    @jwt_required()
    @allow(['admin','customer_service'])
    def delete(self,id):
        user=User.query.filter_by(id=id).first()
        
        if not user or user.role not in ['admin']:
            return make_response({"error": "Invalid user ID or Insufficient user role"}, 400)
        
        userParcel=UserParcelAssignment.query.filter_by(user_id=id).first()
        db.session.delete(userParcel)
        db.session.commit()
        
        return make_response({
            "message":"Assignment is deleted"
        },204)

api.add_resource(Userparcels,'/assignments/<int:id>') 
            
        
if __name__==("__main__"):
    app.run(port=5555,debug=True)       