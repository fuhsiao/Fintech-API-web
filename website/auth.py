from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user

from website.views import Portfolio
from .models import Mapping_code, Users, Invest_plan, Portfolios
from . import db

auth = Blueprint('auth',__name__)

# 登入
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userAccount = request.form.get('userAccount')
        userPwd = request.form.get('userPwd')
        user = Users.query.filter_by(account=userAccount).first()
        if user:
            if check_password_hash(user.password, userPwd):
                print('success')
                login_user(user, remember=True)
                return redirect(url_for('views.Index'))
            else:
                flash('密碼錯誤 ! 請重新輸入', category='error')
        else:
            flash('此帳號不存在', category='error')
    return render_template('login.html')

# 註冊
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # get selector options
    opCode = Mapping_code.query.filter(Mapping_code.category.in_(['op1','op2','op3'])).all()
    options = list(map(lambda Mapping_code:Mapping_code.serialize(),opCode))
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
            new_portfolio = Portfolios(name='我的自選股',user_id=this_user.id)
            db.session.add(new_portfolio)
            db.session.commit()
            flash('註冊成功! 請重新登入', category='success')
            return redirect(url_for('auth.login'))
    return render_template('sign-up.html', options = options)

# 登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))