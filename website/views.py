from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views',__name__)

@views.route('/index')
@login_required
def Index():
    print(current_user.id)
    return render_template("index.html", user = current_user)

@views.route('/target')
@login_required
def Target():
    return render_template('target.html', user = current_user)

@views.route('/portfolio')
@login_required
def Portfolio():
    return render_template('portfolio.html', user = current_user)

@views.route('/picker-oneself')
@login_required
def Picker1():
    return render_template('picker-oneself.html', user = current_user)

@views.route('/picker-cond')
@login_required
def Picker2():
    return render_template('picker-cond.html', user = current_user)

@views.route('/risk-assessment')
@login_required
def Risk_assess():
    return render_template('risk-assessment.html', user = current_user)

@views.route('/account')
@login_required
def Set_account():
    return render_template('account.html', user = current_user)
