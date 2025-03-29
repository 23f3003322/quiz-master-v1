from database import db 

class User(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    username = db.Column(db.String(),unique=True,nullable = False)
    password = db.Column(db.String(),nullable= False)
    fullName = db.Column(db.String(),nullable= False)
    qualification = db.Column(db.String(),nullable= False)
    DOB = db.Column(db.String(),nullable= False)
    role = db.Column(db.String(20), nullable=False, default='user')