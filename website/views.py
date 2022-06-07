from email.policy import default
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from mysqlx import PoolError
from .models import Mapping_code, Invest_plan, Portfolios, Stocks
from . import db
import json

views = Blueprint('views',__name__)


# ===================== Frontend page =====================

# 主頁-儀表板
@views.route('/index')
@login_required
def Index():
    print(current_user.id)
    return render_template("index.html", user = current_user)

# 投資取向
@views.route('/target', methods=['GET','POST'])
@login_required
def Target():
    opCode = Mapping_code.query.filter(Mapping_code.category.in_(['op1','op2','op3'])).all()
    options = list(map(lambda Mapping_code:Mapping_code.serialize(),opCode))
    current_user.investplan = mapping_investplanText(current_user.investplan, options)
    user_plans = list(map(lambda Invest_plan:Invest_plan.serialize(Invest_plan.id),current_user.investplan))
    return render_template('target.html', user = current_user , options = options, user_plans = user_plans )    

# 投資組合
@views.route('/portfolio', defaults={'index':0})
@views.route('/portfolio/<index>')
@login_required
def Portfolio(index):
    user_portfolios = list(map(lambda Portfolios:Portfolios.serialize(Portfolios.id),current_user.portfolios))
    portfolio_index = user_portfolios[int(index)]['id']
    this_portfolio = Portfolios.query.filter_by(id=portfolio_index).first()
    
    current_portfolio = list(map(lambda Stocks:Stocks.serialize(),this_portfolio.selected_stocks))

    return render_template('portfolio.html', user = current_user, user_portfolios = user_portfolios, portfolio = current_portfolio, portfolio_index = index)

# 選股-個人推薦
@views.route('/picker-oneself')
@login_required
def Picker1():
    return render_template('picker-oneself.html', user = current_user)

# 選股-自訂條件
@views.route('/picker-cond')
@login_required
def Picker2():
    return render_template('picker-cond.html', user = current_user)

# 風險評估
@views.route('/risk-assessment')
@login_required
def Risk_assess():
    return render_template('risk-assessment.html', user = current_user)

# 個人資料
@views.route('/account')
@login_required
def Set_account():
    return render_template('account.html', user = current_user)



# ===================== CRUD methods =====================

# 新增計畫 (Target)
@views.route('/add_newPlan', methods=['POST'])
@login_required
def add_newPlan():
    if request.method == 'POST':
        new_planName = request.form.get('new_planName')
        monthlyInvest = request.form.get('monthlyInvest')
        planTime = request.form.get('planTime')
        planRisk = request.form.get('planRisk')
        new_plan = Invest_plan(plan_name=new_planName, plan_monthly_invest=monthlyInvest, plan_time=planTime, plan_risk=planRisk, user_id=current_user.id)
        db.session.add(new_plan)
        db.session.commit()
        return redirect(url_for('views.Target'))
    return jsonify({})

# 刪除計畫 (Target)
@views.route('/delete_plan', methods=['POST'])
@login_required
def delete_Plan():
    plan_id = request.form.get('plan_id')
    plan = Invest_plan.query.get(plan_id)
    if plan.user_id == current_user.id:
        db.session.delete(plan)
        db.session.commit()
    return redirect(url_for('views.Target'))

# 新增投資組合 (Portfolio)
@views.route('/add_portfolio', methods=['POST'])
@login_required
def add_portfolio():
    if request.method == 'POST':
        portfolio_name = request.form.get('portfolio_name')
        new_portfolio = Portfolios(name=portfolio_name, user_id=current_user.id)
        db.session.add(new_portfolio)
        db.session.commit()
    return redirect(url_for('views.Portfolio'))

# 修改組合名稱 (Portfolio)
@views.route('/edit_portfolio_name', methods=['POST'])
@login_required
def edit_portfolio_name():
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        portfolio_index = request.form.get('index')
        portfolio_newName = request.form.get('portfolio_newName')
        portfolio = Portfolios.query.get(portfolio_id)
        if portfolio.user_id == current_user.id:
            portfolio.name = portfolio_newName
            db.session.commit()
    return redirect(url_for('views.Portfolio', index=portfolio_index))
    
# 刪除投資組合 (Portfolio)
@views.route('/delete_portfolio', methods=['POST'])
@login_required
def delete_portfolio():
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        portfolio = Portfolios.query.get(portfolio_id)
        if portfolio.user_id == current_user.id:
            db.session.delete(portfolio)
            db.session.commit()
    return redirect(url_for('views.Portfolio'))

# 新增股票 (Portfolio)
@views.route('/add_stock_by_id', methods=['POST'])
@login_required
def add_stock_by_id():
    if request.method == 'POST':
        stock_id = request.form.get('stock_id')
        stock = Stocks.query.get(stock_id)
        portfolio_index = request.form.get('index')
        portfolio_id = request.form.get('portfolio_id')
        this_portfolio = Portfolios.query.get(portfolio_id)
        if stock and (stock not in this_portfolio.selected_stocks): 
            this_portfolio.selected_stocks.append(stock)
            db.session.commit()
    return redirect(url_for('views.Portfolio',index=portfolio_index))

# 刪除股票 (Portfolio)
@views.route('/delete_stock',methods=['POST'])
@login_required
def delete_stock():
    if request.method == 'POST':    
        stock_id = request.form.get('stock_id')
        stock = Stocks.query.get(stock_id)
        portfolio_index = request.form.get('index')
        portfolio_id = request.form.get('portfolio_id')   
        this_portfolio = Portfolios.query.get(portfolio_id)
        if this_portfolio.user_id == current_user.id:
            this_portfolio.selected_stocks.remove(stock)
            db.session.commit()
    return redirect(url_for('views.Portfolio',index=portfolio_index))

# 投資組合 分頁路由 (Portfolio)
@views.route('/portfolio_index_router', methods=['POST'])
@login_required
def portfolio_index_router():
    portfolio_index = request.form['index']
    return redirect(url_for('views.Portfolio',index=portfolio_index))


# ===================== other methods =====================

# 取得 選項名稱 (by id)
def mapping_codeValue(id, options):
    for i in options:
        if id == i['id']:
            return i['name']
    return ""

# 取得 投資計畫 表格欄的對應名稱
def mapping_investplanText(plans, options):
    for i in plans:
        i.monInvest_text = mapping_codeValue(i.plan_monthly_invest, options)
        i.planTime_text = mapping_codeValue(i.plan_time, options)
        i.planRisk_text = mapping_codeValue(i.plan_risk, options)
    return plans