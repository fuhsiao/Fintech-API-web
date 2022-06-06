from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy
from . import db

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(120))
    name = db.Column(db.String(20))
    email = db.Column(db.String(45))
    investplan = db.relationship('Invest_plan',  backref='Users')
    portfolio = db.relationship('Portfolio', backref='Users')

class Invest_plan(db.Model):
    __tablename__ = 'invest_plan'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    plan_name = db.Column(db.String(45))
    plan_monthly_invest = db.Column(db.Integer)
    plan_time = db.Column(db.Integer)
    plan_risk = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 預留 3 空字串(選項文字)
    monInvest_text=''
    planTime_text=''
    planRisk_text=''

    def __init__(self, plan_name, plan_monthly_invest, plan_time, plan_risk, monInvest_text="", planTime_text="", planRisk_text="", user_id=""):
        self.plan_name = plan_name
        self.plan_monthly_invest = plan_monthly_invest
        self.plan_time = plan_time
        self.plan_risk = plan_risk
        self.monInvest_text = monInvest_text
        self.planTime_text = planTime_text
        self.planRisk_text = planRisk_text
        self.user_id = user_id

    # plam_id 序列化時在傳入(寫在__init__會變必傳參數，但 id 為 AI-PK 不用傳入)
    def serialize(self, plan_id):
        return{
            "id":plan_id,
            "planName":self.plan_name,
            "monInvest":self.plan_monthly_invest,
            "planTime":self.plan_time,
            "planRisk":self.plan_risk,
            "monInvest_text":self.monInvest_text,
            "planTime_text":self.planTime_text,
            "planRisk_text":self.planRisk_text
        }


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def serialize(self, portfolio_id):
        return{
            "id":portfolio_id,
            "name":self.name
        }

class Mapping_code(db.Model):
    __tablename__ = 'mapping_code'
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