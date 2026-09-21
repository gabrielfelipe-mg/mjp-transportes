import calendar
from datetime import datetime
from flask import redirect, render_template, request, session, url_for
from models import Caminhao
from principal import app, db
from sqlalchemy import func


@app.route("/relatorio-ganhos")
def relatorio_ganhos():
    if not session.get("usuario_logado"):
        return redirect(url_for("login"))

    hoje = datetime.now()
    quinzena = request.args.get("quinzena", "1")
    mes = int(request.args.get("mes", hoje.month))
    ano = int(request.args.get("ano", hoje.year))

    if quinzena == "1":
        data_inicio = datetime(ano, mes, 1, 0, 0, 0)
        data_fim = datetime(ano, mes, 15, 23, 59, 59)
    elif quinzena == "2":
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        data_inicio = datetime(ano, mes, 16, 0, 0, 0)
        data_fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)
    else:
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        data_inicio = datetime(ano, mes, 1, 0, 0, 0)
        data_fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)

    resumo_ganhos = (
        db.session.query(
            Caminhao.nomeMotorista,
            func.sum(Caminhao.ganhoMotorista).label("total_ganho"),
            func.sum(Caminhao.valorViagem).label("total_faturamento"),
            func.count(Caminhao.id).label("total_viagens"),
        )
        .filter(
            Caminhao.data_viagem >= data_inicio,
            Caminhao.data_viagem <= data_fim,
        )
        .group_by(Caminhao.nomeMotorista)
        .order_by(Caminhao.nomeMotorista)
        .all()
    )

    total_geral_ganhos = sum(row.total_ganho or 0 for row in resumo_ganhos)
    total_geral_faturamento = sum(
        row.total_faturamento or 0 for row in resumo_ganhos
    )
    total_geral_viagens = sum(row.total_viagens or 0 for row in resumo_ganhos)

    return render_template(
        "relatorio_ganhos.html",
        titulo="Relatório de Ganhos dos Motoristas",
        resumo=resumo_ganhos,
        total_geral=total_geral_ganhos,
        total_faturamento_geral=total_geral_faturamento,
        total_viagens_geral=total_geral_viagens,
        quinzena_selecionada=quinzena if quinzena == "todas" else int(quinzena),
        mes_selecionado=mes,
        ano_selecionado=ano,
    )