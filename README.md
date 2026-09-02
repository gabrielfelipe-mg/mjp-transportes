<div align="center">

# 🚚 MJP Transportes — Gestão de Frota e Logística

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

Sistema web full-stack desenvolvido para gerenciamento de viagens de carga, controle de manifestos, suporte a múltiplas lojas e cálculo automatizado de comissões de motoristas.

</div>

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, Flask, SQLAlchemy (ORM)
- **Frontend:** HTML5, Jinja2, Bootstrap 5, Bootstrap Icons
- **Banco de Dados:** MySQL (comunicação relacional)
- **Segurança & Formulários:** Flask-Bcrypt (criptografia de senhas), WTForms (validação e proteção CSRF)

---

## ✨ Funcionalidades Principais

- **🔒 Autenticação Segura:** Sistema de login protegido com armazenamento de senhas via hash Bcrypt.
- **🚛 Gestão Completa de Viagens (CRUD):** Cadastro, listagem, edição e exclusão de viagens e manifestos de transporte.
- **🏬 Suporte Multi-Loja:** Registro flexível de atendimentos cobrindo diferentes lojas em uma mesma operação.
- **💰 Cálculo de Comissão:** Aplicação automática da regra de negócio de **13% sobre o valor da viagem** para o motorista.
- **📊 Relatório de Ganhos Consolidados:** Agrupamento e soma em tempo real do faturamento bruto e das comissões pagas por motorista.
- **📱 Interface Responsiva:** Layout adaptado para navegação em dispositivos móveis e desktops.

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado.
- Servidor MySQL em execução.

### Passo a passo

1. **Clone o repositório:**
   git clone https://github.com/gabrielfelipe-mg/mjp-transportes.git
   cd mjp-transportes

2. **Crie e ative o ambiente virtual:**
   python -m venv .venv
   .venv\Scripts\activate

3. **Instale as dependências:**
   pip install -r requirements.txt

4. **Configure o Banco de Dados MySQL:**
   - Crie o banco de dados MySQL e atualize a URI de conexão no arquivo de configuração do projeto (config.py).

5. **Inicie a aplicação:**
   python principal.py

6. **Acesse no navegador:**
   - Navegue até http://127.0.0.1:5000

---

## 🤝 Autor

Desenvolvido por **Gabriel Felipe Pereira da Silveira**.

- **GitHub:** [@gabrielfelipe-mg](https://github.com/gabrielfelipe-mg)