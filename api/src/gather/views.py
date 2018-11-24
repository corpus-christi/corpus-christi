from flask import render_template

from . import gather


@gather.route('/')
def index():
    return render_template('gather.html')
