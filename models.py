from datetime import datetime
from decimal import Decimal
from sqlalchemy.event import listens_for
from principal import db


class Caminhao(db.Model):
    __tablename__ = 'info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_viagem = db.Column(db.DateTime, nullable=False, default=datetime.now)
    manifesto = db.Column(db.Integer, nullable=False)
    placa = db.Column(db.String(10), nullable=False)
    nomeMotorista = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(120), nullable=False)
    numeroLoja = db.Column(db.String(50), nullable=False)
    valorViagem = db.Column(db.Numeric(10, 2), nullable=False)
    ganhoMotorista = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return '<Motorista {}>'.format(self.nomeMotorista)


@listens_for(Caminhao.valorViagem, 'set')
def calcular_ganho(target, valor, valorAntigo, inicializador):
    if valor is not None:
        if isinstance(valor, str):
            valor = valor.replace(',', '.').strip()
            valor = Decimal(valor) if valor else Decimal('0.00')
        elif isinstance(valor, (int, float)):
            valor = Decimal(str(valor))
        target.ganhoMotorista = round(valor * Decimal('0.13'), 2)


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_usuario = db.Column(db.String(50), nullable=False)
    login_usuario = db.Column(db.String(50), nullable=False)
    senha = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Usuario {}>'.format(self.nome_usuario)


class LancamentoContabilidade(db.Model):
  __tablename__ = 'lancamentos_contabilidade'

  id = db.Column(db.Integer, primary_key=True)
  data_movimentacao = db.Column(db.Date, nullable=False)
  numero_documento = db.Column(db.String(50))
  favorecido = db.Column(db.String(255))
  cpf_cnpj = db.Column(db.String(20))
  descricao = db.Column(db.Text)
  valor = db.Column(db.Numeric(10, 2), nullable=False)
  tipo = db.Column(db.String(20), nullable=False)
  conta_origem = db.Column(db.String(100))
  hash_transacao = db.Column(db.String(32), unique=True, nullable=False)