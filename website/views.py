from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import Mapping_code

views = Blueprint('views',__name__)

@views.route('/index')
@login_required
def Index():
    print(current_user.id)
    return render_template("index.html", user = current_user)

@views.route('/target')
@login_required
def Target():
    # get selector options
    opCode = Mapping_code.query.filter(Mapping_code.category.in_(['op1','op2','op3'])).all()
    options = list(map(lambda Mapping_code:Mapping_code.serialize(),opCode))
    return render_template('target.html', user = current_user , options = options)

@views.route('/addnewPlan', methods=['GET','POST'])
@login_required
def Add_newPlan():
    print('dsaas')
    if request.method == 'POST':
        return redirect(url_for('views.Target'))


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
