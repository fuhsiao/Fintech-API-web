from flask import Blueprint, render_template

views = Blueprint('views',__name__)

@views.route('/index')
def Index():
    return render_template("index.html")

@views.route('/target')
def Target():
    return render_template('target.html')

@views.route('/portfolio')
def Portfolio():
    return render_template('portfolio.html')

@views.route('/picker-oneself')
def Picker1():
    return render_template('picker-oneself.html')

@views.route('/picker-cond')
def Picker2():
    return render_template('picker-cond.html')

@views.route('/risk-assessment')
def Risk_assess():
    return render_template('risk-assessment.html')

@views.route('/account')
def Set_account():
    return render_template('account.html')
