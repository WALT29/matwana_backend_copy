from models import db,User,Parcel,Vehicle,Location,UserParcelAssignment
from app import app

with app.app_context():
    db.drop_all()
    db.create_all()