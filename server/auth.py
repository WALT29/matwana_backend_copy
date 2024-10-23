from models import User,db,TokenBlocklist
from flask import Blueprint,request,make_response
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token,create_refresh_token,JWTManager,get_jwt,current_user,jwt_required,get_jwt_identity
from functools import wraps
from datetime import datetime, timezone

jwt=JWTManager()

auth_bp = Blueprint('auth_bp',__name__, url_prefix='/auth')
api=Api(auth_bp)



def allow(required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            jwt_claims=get_jwt()
            user_role=jwt_claims.get('role',None)
            
            if user_role not in required_roles:
                return make_response({
                    "error":"Access forbidden"
                },403)
            return func(*args,**kwargs)
        return wrapper
    return decorator

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header,jwt_data):
    identity=jwt_data['sub']
    return User.query.filter_by(id=identity).first()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_data):
    jti = jwt_data["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()

    return token or None



class Signup(Resource):
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

class Login(Resource):
    def post(self):
        data=request.get_json()
        phone_number=data['phone_number']
        password=data['password']
        
        user=User.get_user_by_phone(phone_number=phone_number)
        
        
        if user and (user.check_password(password=password)):
            access_token=create_access_token(identity=user.id,additional_claims={"role":user.role})
            refresh_token=create_refresh_token(identity=user.id)
            
            return make_response({
                "message":"logged in successfully",
                "tokens":{
                    "access_token":access_token,
                    "refresh_token":refresh_token
                },
                "role":user.role,
                "id":user.id
            },200)
        
        else:
            return make_response({
                "message":"Invalid username or password"
            },200)
    @jwt_required(refresh=True)
    def get(self):
        identity=get_jwt_identity
        new_access_token=create_access_token(identity=identity)
        
        return make_response({
            "access_token":new_access_token
        })

class UserIdentity(Resource):
    @jwt_required()
    def get(self):
        return make_response({
            "user details":{
                "name":current_user.name,
                "role":current_user.role
            }
        },200)

class Logout(Resource):
    
    @jwt_required()
    def get(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        
        return make_response(
            {"message": "You have been logged out"},
            200
        )

api.add_resource(Login,'/login')
api.add_resource(Signup,'/signup')
api.add_resource(UserIdentity,'/useridentity')
api.add_resource(Logout,'/logout')

        
        