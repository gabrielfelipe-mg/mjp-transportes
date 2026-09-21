from flask import render_template, request, redirect, session, flash, url_for
from definicoes import FormularioViagens
from principal import db, app
from models import  Caminhao


@app.route("/")
def listar_viagens():
    if "usuario_logado" not in session or session["usuario_logado"] is None:
        return redirect(url_for("login"))

    page = request.args.get("page", 1, type=int)

    per_page = 10

    lista = Caminhao.query.order_by(Caminhao.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "lista_viagens.html", titulo="Viagens Cadastradas", viagens=lista
    )

@app.route('/cadastro')
def cadastro_viagens():
    if session['usuario_logado'] == None or 'usuario_logado' not in session:
        return redirect(url_for('login'))
    form = FormularioViagens()
    return render_template('cadastro_viagens.html', titulo="Cadastrar Viagens", form=form)

@app.route('/adicionar', methods=['POST',])
def adicionar_viagens():
    formRecebido = FormularioViagens(request.form)
    if not formRecebido.validate_on_submit():
        return redirect(url_for('cadastro_viagens'))
    placa = formRecebido.placa.data
    nome = formRecebido.nome.data
    valor = formRecebido.valorViagem.data
    cidade = formRecebido.cidade.data
    loja = formRecebido.loja.data
    manifesto = formRecebido.manifesto.data
    viagem = Caminhao.query.filter_by(manifesto=manifesto).first()
    if viagem:
        flash("Viagem já está cadastrada!")
        return redirect(url_for('listar_viagens'))
    nova_viagem = Caminhao(placa=placa,nomeMotorista=nome,valorViagem=valor,cidade=cidade,numeroLoja=loja, manifesto=manifesto)
    db.session.add(nova_viagem)
    db.session.commit()
    return redirect(url_for('listar_viagens'))

@app.route('/editar/<int:id_viagem>')
def editar_viagens(id_viagem):
    if session['usuario_logado'] == None or 'usuario_logado' not in session:
        return redirect(url_for('login'))
    buscar_viagem = Caminhao.query.filter_by(id=id_viagem).first()
    form = FormularioViagens()
    form.placa.data = buscar_viagem.placa
    form.nome.data = buscar_viagem.nomeMotorista
    form.valorViagem.data = buscar_viagem.valorViagem
    form.cidade.data = buscar_viagem.cidade
    form.loja.data = buscar_viagem.numeroLoja
    form.manifesto.data = buscar_viagem.manifesto
    return render_template ('editar_viagens.html', titulo="Editar Viagem", viagem=form, id_viagem=id_viagem)

@app.route('/atualizar', methods=['POST',])
def atualizar_viagens():
    if not session.get('usuario_logado'):
        return redirect(url_for('login'))
    id_viagem = request.form.get('txtId')
    viagem = db.session.get(Caminhao, id_viagem) if id_viagem else None
    if not viagem:
        flash(f"Erro: Viagem não encontrada (ID recebido: '{id_viagem}').")
        return redirect(url_for('listar_viagens'))
    formRecebido = FormularioViagens(request.form)
    viagem.manifesto = formRecebido.manifesto.data
    viagem.placa = formRecebido.placa.data
    viagem.nomeMotorista = formRecebido.nome.data
    viagem.cidade = formRecebido.cidade.data
    viagem.numeroLoja = formRecebido.loja.data
    viagem.valorViagem = formRecebido.valorViagem.data
    db.session.commit()
    flash("Viagem atualizada com sucesso!")
    return redirect(url_for('listar_viagens'))


@app.route('/excluir/<int:id_viagem>')
def excluir_viagens(id_viagem):
    if session['usuario_logado'] == None or 'usuario_logado' not in session:
        return redirect(url_for('login'))
    Caminhao.query.filter_by(id=id_viagem).delete()
    db.session.commit()
    flash("Viagem excluida com sucesso!")
    return redirect(url_for('listar_viagens'))

