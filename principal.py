from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

csrf = CSRFProtect(app)

from views_viagens import *
from views_usuario import *
from views_financeiro import *
from views_relatorio_ganhos import *

if __name__ == '__main__':
    app.run(debug=True)

