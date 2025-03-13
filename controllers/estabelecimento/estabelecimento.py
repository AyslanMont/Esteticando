from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required

estabelecimento_bp = Blueprint('estabelecimento', __name__, url_prefix='/estabelecimento', template_folder='template')


@estabelecimento_bp.route('/estabelecimento')
@login_required
def estabelecimento():
    return render_template('estabelecimento.html')


@estabelecimento_bp.route('/resu_estabelecimento')
@login_required
def resu_estabelecimento():
    return render_template('resu_estabelecimento.html')


@estabelecimento_bp.route('/dentro_estabelecimento')
@login_required
def dentro_estabelecimento():
    return render_template('dentro_estabelecimento.html')
