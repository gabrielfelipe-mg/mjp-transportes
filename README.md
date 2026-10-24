# 🚚 MJP Transportes — Gestão de Frota, Logística e Finanças

Sistema web *full-stack* para gerenciamento operacional e financeiro de empresas de transporte rodoviário de cargas. Controla viagens e manifestos, calcula automaticamente a comissão dos motoristas e importa extratos bancários para conciliação financeira.

Projeto criado a partir de uma necessidade real da operação: o fechamento mensal era feito em planilhas, com retrabalho e risco de erro de cálculo.

---

## 🛠️ Tecnologias

* **Backend:** Python 3, Flask, SQLAlchemy (ORM)
* **Processamento de dados:** Pandas, ofxparse, openpyxl
* **Frontend:** HTML5, CSS3, Jinja2, Bootstrap 5
* **Banco de dados:** MySQL
* **Segurança:** Flask-Bcrypt (hash de senhas), Flask-WTF (validação e proteção CSRF), variáveis de ambiente para credenciais

---

## ✨ Funcionalidades

* 🔒 **Autenticação:** login com senhas armazenadas como hash e rotas protegidas por verificação de sessão.
* 🚛 **Viagens e manifestos (CRUD):** cadastro, listagem, edição e exclusão.
* 🏬 **Multi-loja:** vários clientes e lojas na mesma operação.
* 💵 **Comissão automática:** 13% do valor do frete, calculada com `Decimal` para evitar erros de arredondamento.
* 📊 **Conciliação financeira:**
  * Importação de extratos bancários no formato **OFX**, sem duplicar lançamentos (hash único por transação).
  * Classificação de recebimentos e pagamentos.
  * Lançamentos manuais de despesas e receitas.
  * Exportação para **Excel (.xlsx)** e visão para impressão/PDF.
* 📱 **Interface responsiva** para desktop e celular.

---

## 🚀 Como executar localmente

### Pré-requisitos

* Python 3.10 ou superior
* Servidor MySQL em execução

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/gabrielfelipe-mg/mjp-transportes.git
   cd mjp-transportes
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:** copie `.env.example` para `.env` e preencha:
   ```
   SECRET_KEY=uma_chave_longa_e_aleatoria
   DB_SGBD=mysql+mysqlconnector
   DB_USER=seu_usuario_mysql
   DB_PASSWORD=sua_senha_mysql
   DB_HOST=localhost
   DB_NAME=nome_do_banco
   FLASK_DEBUG=0
   ```
   Para gerar uma `SECRET_KEY`:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Crie o banco e as tabelas:**
   ```sql
   CREATE DATABASE nome_do_banco CHARACTER SET utf8mb4;
   ```
   Depois, com o `.env` preenchido, rode:
   ```bash
   python criar_banco.py
   ```
   O script cria as tabelas e pede os dados do primeiro usuário.

6. **Execute o sistema:**
   ```bash
   python principal.py
   ```
   Acesse `http://127.0.0.1:5000`.

---

## 🔐 Segurança

* Senhas nunca são guardadas em texto puro (hash bcrypt).
* Credenciais ficam em variáveis de ambiente, fora do código.
* Proteção CSRF nos formulários e consultas parametrizadas via ORM.
* Todas as rotas, exceto o login, exigem usuário autenticado.
* O modo debug do Flask fica desligado por padrão.

---

## 🧭 Próximos passos

* Testes automatizados com `pytest`
* Padronizar `Decimal` também no módulo de extratos
* Migrações de banco com Flask-Migrate
* Perfis de acesso (administrador e operador)

---

## 👤 Autor

**Gabriel Felipe** — [LinkedIn](https://linkedin.com/in/gabriel-felipe-7a93ab2b7) · [GitHub](https://github.com/gabrielfelipe-mg)