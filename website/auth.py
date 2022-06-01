from flask import Blueprint, render_template
from .models import Mapping_code

auth = Blueprint('auth',__name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/sign-up')
def sign_up():
    # option = Mapping_code.query.filter(Mapping_code.category.in_(['op1','op2','op3'])).all()
    option1 = Mapping_code.query.filter(Mapping_code.category == 'op1').all()
    option2 = Mapping_code.query.filter(Mapping_code.category == 'op2').all()
    option3 = Mapping_code.query.filter(Mapping_code.category == 'op3').all()
    return render_template('sign-up.html', op1 = option1, op2 = option2 , op3 = option3)