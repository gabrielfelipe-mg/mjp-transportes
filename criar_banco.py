from flask_bcrypt import generate_password_hash

from principal import app, db
from models import Usuario

with app.app_context():
    db.create_all()
    print("Tabelas criadas (as que já existiam foram mantidas).")

    if Usuario.query.count() == 0:
        print("\nNenhum usuário cadastrado. Vamos criar o primeiro.")
        nome = input("Nome: ").strip()
        login = input("Login: ").strip()
        senha = input("Senha: ")
        hash_senha = generate_password_hash(senha).decode('utf-8')
        db.session.add(Usuario(nome_usuario=nome, login_usuario=login, senha=hash_senha))
        db.session.commit()
        print("Usuário criado com sucesso.")