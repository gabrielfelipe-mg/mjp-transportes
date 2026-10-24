# 🚚 MJP Transportes — Gestão de Frota, Logística e Finanças

Sistema web *full-stack* desenvolvido para gerenciamento operacional e financeiro de empresas de transporte rodoviário de cargas. Permite o controle completo de viagens, manifesto de cargas, cálculo automatizado de comissões de motoristas e importação de extratos bancários para conciliação financeira.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3, Flask, SQLAlchemy (ORM)
* **Processamento de Dados:** Pandas
* **Frontend:** HTML5, CSS3, Jinja2, Bootstrap 5, Bootstrap Icons
* **Banco de Dados:** MySQL (comunicação relacional)
* **Segurança & Formulários:** Werkzeug / Flask-Bcrypt (criptografia de senhas), WTForms (validação e proteção CSRF)

---

## ✨ Funcionalidades Principais

* 🔒 **Autenticação Segura:** Sistema de login protegido com verificação e armazenamento de senhas via hash criptográfico.
* 🚛 **Gestão Completa de Viagens (CRUD):** Cadastro, listagem, edição e exclusão de viagens e manifestos de transporte.
* 🏬 **Suporte Multi-Loja:** Registro flexível de atendimentos cobrindo diferentes lojas e clientes em uma mesma operação.
* 💵 **Cálculo de Comissão:** Aplicação automática da regra de negócio de 13% sobre o valor do frete para o motorista.
* 📊 **Relatórios e Conciliação Financeira:**
  * Importação e processamento automatizado de extratos bancários no formato **.OFX**.
  * Classificação de recebimentos e pagamentos por conta de origem.
  * Lançamentos manuais de despesas e receitas.
  * Exportação de relatórios consolidados em **Excel (.xlsx)** e visão otimizada para **impressão/PDF**.
* 📱 **Interface Responsiva:** Layout adaptado para navegação em desktops e dispositivos móveis.

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos

* Python 3.10 ou superior instalado.
* Servidor MySQL em execução.

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/gabrielfelipe-mg/mjp-transportes.git](https://github.com/gabrielfelipe-mg/mjp-transportes.git)
   cd mjp-transportes
