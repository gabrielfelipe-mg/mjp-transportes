from flask_wtf import FlaskForm
from wtforms import StringField, validators, IntegerField, SubmitField, DecimalField
from wtforms.fields.simple import PasswordField


class FormularioViagens(FlaskForm):
    manifesto = IntegerField('Manifesto', validators=[validators.DataRequired(),
                                                      validators.NumberRange(min=1)])
    placa = StringField('Placa', validators=[validators.DataRequired(),
                                             validators.Length(min=1, max=10)])
    nome = StringField('Nome do Motorista', validators=[validators.DataRequired()
                                                        , validators.Length(min=2, max=100)])
    cidade = StringField('Cidade', validators=[validators.DataRequired(),
                                               validators.Length(min=1, max=120)])
    loja = StringField('Loja', validators=[validators.DataRequired(),
                                            validators.Length(min=1)])
    valorViagem = DecimalField('Valor da Viagem', validators=[validators.DataRequired(),
                                                           validators.NumberRange(min=0.01)])
    cadastrar = SubmitField('Cadastrar Viagem')


class FormularioUsuario(FlaskForm):
    login = StringField('Usuário', validators=[validators.DataRequired(),
                                             validators.Length(min=2, max=50)])
    senha = PasswordField('Senha', validators=[validators.DataRequired(),
                                               validators.Length(min=4, max=255)])
    entrar = SubmitField('Entrar')

class FormularioCadastroUsuario(FlaskForm):
    nome = StringField('Nome', validators=[validators.DataRequired(),
                                                      validators.Length(min=2, max=50)])
    usuario = StringField('Usuario', validators=[validators.DataRequired(),
                                                 validators.Length(min=2, max=50)])
    senha = PasswordField('Senha', validators=[validators.DataRequired(),
                                               validators.Length(min=4, max=255)])
    cadastrar = SubmitField('Cadastrar Usuário')