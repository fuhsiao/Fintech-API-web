from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Mapping_code, Users, Invest_plan
from . import db

auth = Blueprint('auth',__name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # get selector options
    opCode = Mapping_code.query.filter(Mapping_code.category.in_(['op1','op2','op3'])).all()
    options = list(map(lambda Mapping_code:Mapping_code.serialize(),opCode))
    # get form data
    if request.method == 'POST':
        planName = request.form.get('planName')
        monthlyInvest = request.form.get('monthlyInvest')
        planTime = request.form.get('planTime')
        planRisk = request.form.get('planRisk')
        userName = request.form.get('userName')
        userAccount = request.form.get('userAccount')
        userPwd = request.form.get('userPwd')
        userPwdConfirm = request.form.get('userPwdConfirm')

        # check if account exists
        user = Users.query.filter_by(account=userAccount).first()

        if user:
            flash('此帳號已存在!', category='error')
        elif len(userAccount) < 5:
            flash('帳號至少需要 5 個字元', category='error')
        elif userPwd != userPwdConfirm:
            flash('密碼輸入不一致', category='error')
        elif len(userPwd) < 7:
            flash('密碼至少要 7 個字元', category='error')
        else:
            # add user
            new_user = Users(account=userAccount, password=generate_password_hash(userPwd, method='sha256'), name=userName)
            db.session.add(new_user)
            db.session.commit()
            # add this user's plan
            this_user = Users.query.with_entities(Users.id).filter_by(account=userAccount).first() 
            new_plan = Invest_plan(plan_name=planName, plan_monthly_invest=monthlyInvest, plan_time=planTime, plan_risk=planRisk, user_id=this_user.id)
            db.session.add(new_plan)
            db.session.commit()
            flash('註冊成功! 請重新登入', category='success')
            return redirect(url_for('auth.login'))
    
    return render_template('sign-up.html', options = options)