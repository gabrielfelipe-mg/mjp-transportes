import os

from flask import Flask, request, session, redirect, url_for

from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

@app.before_request
def exigir_login():
    rotas_publicas = {'login', 'autenticar', 'static'}
    if request.endpoint is None or request.endpoint in rotas_publicas:
        return
    if not session.get('usuario_logado'):
        return redirect(url_for('login'))

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

csrf = CSRFProtect(app)

from views_viagens import *
from views_usuario import *
from views_financeiro import *
from views_relatorio_ganhos import *

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')

