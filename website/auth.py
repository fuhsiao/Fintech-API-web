from click import option
from flask import Blueprint, render_template
from .models import Mapping_code

auth = Blueprint('auth',__name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/sign-up')
def sign_up():
    data = Mapping_code.query.filter(Mapping_code.category.in_(['op1','op2','op3'])).all()
    options = list(map(lambda Mapping_code:Mapping_code.serialize(),data))
    return render_template('sign-up.html', options = options)