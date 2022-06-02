from flask_login import UserMixin
from . import db

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(120))
    name = db.Column(db.String(20))
    email = db.Column(db.String(45))
    # investplan = db.relationship('Invest_plan')

class Invest_plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(45))
    plan_monthly_invest = db.Column(db.Integer)
    plan_time = db.Column(db.Integer)
    plan_risk = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Mapping_code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    category = db.Column(db.String(45))

    def __init__(self, id, name, category):
        self.id = id
        self.name = name
        self.category = category

    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "category":self.category
        }