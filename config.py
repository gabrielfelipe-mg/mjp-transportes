SECRET_KEY='mjp_transportes'

SQLALCHEMY_DATABASE_URI = '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
    SGBD='mysql+mysqlconnector',
    usuario='root',
    senha='gabrielfps123',
    servidor='localhost',
    database='viagens'
)