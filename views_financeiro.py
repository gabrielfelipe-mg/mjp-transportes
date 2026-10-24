import hashlib
import io
import re
import unicodedata
from datetime import datetime
from flask import flash, redirect, render_template, request, send_file, url_for
from ofxparse import OfxParser
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd

from models import LancamentoContabilidade
from principal import app, db


def extrair_e_limpar_documentos_e_prefixos(texto):
  """Limpa completamente o texto do OFX, removendo CPF/CNPJ, prefixos operacionais

  e qualquer código de estabelecimento/agência do início.
  """
  if not texto:
    return '', ''

  # 1. REMOÇÃO DE CARACTERES INVISÍVEIS E NORMALIZAÇÃO UNICODE
  texto_str = str(texto)
  # Normaliza caracteres especiais e substitui espaço não-quebrável \xa0 por espaço comum
  texto_str = unicodedata.normalize('NFKC', texto_str)
  texto_str = texto_str.replace('\xa0', ' ').replace('\t', ' ')
  texto_str = re.sub(r'[\r\n]+', ' ', texto_str)
  texto_limpo = re.sub(r'\s+', ' ', texto_str).strip()

  # 2. EXTRAÇÃO DE CPF / CNPJ VÁLIDO
  doc_match = re.search(
      r'(\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b)',
      texto_limpo,
  )
  if not doc_match:
    doc_match = re.search(r'\b\d{14}\b|\b\d{11}\b', texto_limpo)

  documento_extraido = doc_match.group(0) if doc_match else ''

  # 3. REMOÇÃO DE CPF E CNPJ DO TEXTO
  texto_limpo = re.sub(
      r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b',
      '',
      texto_limpo,
      flags=re.IGNORECASE,
  )
  texto_limpo = re.sub(
      r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '', texto_limpo, flags=re.IGNORECASE
  )
  texto_limpo = re.sub(
      r'\b\d{11,14}\b', '', texto_limpo, flags=re.IGNORECASE
  )

  # 4. REMOÇÃO DE RÓTULOS RESIDUAIS DE DOCUMENTOS E CÓDIGOS DE INÍCIO
  texto_limpo = re.sub(
      r'\b(CPF/CNPJ|CNPJ/CPF|CPF|CNPJ)[:\s]*',
      '',
      texto_limpo,
      flags=re.IGNORECASE,
  )
  texto_limpo = re.sub(r'^[\d\.\/\-]+\s*', '', texto_limpo)

  # 5. LISTA DE PADRÕES DE PREFIXO BANCÁRIO
  padroes_prefixo = [
      r'^\s*S\s*PIX\s*QR\s*[-]*\s*CODE\s*[-:]?\s*',  # Captura "S PIX QR-CODE", "S PIX QR CODE", "SPIXQRCODE"
      r'^\s*PIX\s*QR\s*[-]*\s*CODE\s*[-:]?\s*',  # Captura "PIX QR-CODE", "PIX QRCODE"
      r'^\s*S\s+PIX\s*[-:]?\s*',  # Captura "S PIX"
      r'^\s*PIX\s+RECEBID[OA]\s*[-:]?\s*',
      r'^\s*PIX\s+ENVIAD[OA]\s*[-:]?\s*',
      r'^\s*PIX\s+TRANSF\s+[A-Z0-9_-]+\s*[-:]?\s*',
      r'^\s*PIX\s+TRANSF\s*[-:]?\s*',
      r'^\s*PIX\s+PAGTO\s*[-:]?\s*',
      r'^\s*PIX\s+PAYMENT\s*[-:]?\s*',
      r'^\s*PIX\s*[-:]?\s*',
      r'^\s*TED\s+RECEBIDA\s*[-:]?\s*',
      r'^\s*TED\s+STR\s*[-:]?\s*',
      r'^\s*TED\s*[-:]?\s*',
      r'^\s*DOC\s*[-:]?\s*',
      r'^\s*BOLETO\s+PAGO\s*[-:]?\s*',
      r'^\s*PAGAMENTO\s+DE\s+BOLETO\s*[-:]?\s*',
      r'^\s*PAGTO\s+BOLETO\s*[-:]?\s*',
      r'^\s*PAG\s+BOLETO\s*[-:]?\s*',
      r'^\s*TITULO\s+PAGO\s*[-:]?\s*',
      r'^\s*PAGTO\s+TITULO\s*[-:]?\s*',
      r'^\s*PAGAMENTO\s+ELETRONICO\s*[-:]?\s*',
      r'^\s*PAGTO\s+ELETRONICO\s*[-:]?\s*',
      r'^\s*PAGAMENTO\s*[-:]?\s*',
      r'^\s*PAGTO\s*[-:]?\s*',
      r'^\s*PAG\s*[-:]?\s*',
      r'^\s*SISPAG\s*[-:]?\s*',
      r'^\s*DEBITO\s+AUTOMATICO\s*[-:]?\s*',
      r'^\s*DB\s+AUTO\s*[-:]?\s*',
      r'^\s*OU\s+[-:]?\s*',
      r'^\s*INT\s+[-:]?\s*',
  ]

  # Processa repetidamente enquanto encontrar algum prefixo no início (limpeza em camadas)
  alterado = True
  while alterado:
    texto_antes = texto_limpo
    for padrao in padroes_prefixo:
      texto_limpo = re.sub(padrao, '', texto_limpo, flags=re.IGNORECASE).strip()
    # Remove eventuais números de agência/código que surgiram após a remoção do prefixo
    texto_limpo = re.sub(r'^[\d\.\/\-]+\s*', '', texto_limpo).strip()
    alterado = texto_antes != texto_limpo

  # 6. REMOÇÃO DE PALAVRAS DUPLICADAS / TRUNCADAS
  texto_limpo = re.sub(
      r'\bSUPERMERCAD\s+SUPERMERCADOS\b',
      'SUPERMERCADOS',
      texto_limpo,
      flags=re.IGNORECASE,
  )

  # 7. LIMPEZA FINAL DE PONTUAÇÃO RESIDUAL
  texto_limpo = re.sub(r'^\s*[-:/.]+\s*', '', texto_limpo)
  texto_limpo = re.sub(r'\s*[-:/.]+\s*$', '', texto_limpo)
  texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()

  return texto_limpo, documento_extraido


@app.route('/financeiro', methods=['GET', 'POST'])
def financeiro():
  if request.method == 'POST':
    file = request.files.get('arquivo_ofx')
    conta_origem = request.form.get('conta_origem', 'Itaú CC')

    if not file or not file.filename.lower().endswith('.ofx'):
      flash('Por favor, envie um arquivo .OFX válido.', 'danger')
      return redirect(url_for('financeiro'))

    try:
      conteudo_bytes = file.read()
      conteudo_texto = None
      for encoding in ['cp1252', 'iso-8859-1', 'latin-1', 'utf-8']:
        try:
          conteudo_texto = conteudo_bytes.decode(encoding)
          break
        except (UnicodeDecodeError, UnicodeError):
          continue

      if conteudo_texto is None:
        conteudo_texto = conteudo_bytes.decode('latin-1', errors='replace')

      conteudo_texto = re.sub(
          r'ENCODING:[^\r\n]+', 'ENCODING:UTF-8', conteudo_texto, flags=re.IGNORECASE
      )
      conteudo_texto = re.sub(
          r'CHARSET:[^\r\n]+', 'CHARSET:1252', conteudo_texto, flags=re.IGNORECASE
      )

      string_io = io.StringIO(conteudo_texto)
      ofx = OfxParser.parse(string_io)

      novos_registros = 0
      duplicados = 0

      encargos_bancarios = [
          'JUROS',
          'TARIFA',
          'TAR',
          'IOF',
          'MORA',
          'ENCARGO',
          'PAC FROTAS',
          'MANUTENCAO',
      ]

      for tx in ofx.account.statement.transactions:
        payee = str(getattr(tx, 'payee', '') or '').strip()
        memo = str(getattr(tx, 'memo', '') or '').strip()
        name = str(getattr(tx, 'name', '') or '').strip()

        texto_completo = f'{payee} {memo} {name}'.strip()

        # FILTRO DE SEGURANÇA: Ignora saldos e resumos
        palavras_saldo = [
            'SALDO',
            'SD DO DIA',
            'SALDO DISPONIVEL',
            'SALDO ANTERIOR',
            'S D O',
            'BALAMT',
            'SALDO FINAL',
        ]
        if any(palavra in texto_completo.upper() for palavra in palavras_saldo):
          continue

        valor = float(tx.amount)
        tipo = 'PAGAMENTO' if valor < 0 else 'RECEBIMENTO'
        valor_absoluto = abs(valor)
        data = tx.date.date()
        numero_doc = tx.checknum or tx.id or 'S/N'

        # Limpeza individual e combinada
        texto_geral_limpo, doc_geral = extrair_e_limpar_documentos_e_prefixos(
            texto_completo
        )
        payee_limpo, doc_payee = extrair_e_limpar_documentos_e_prefixos(payee)
        memo_limpo, doc_memo = extrair_e_limpar_documentos_e_prefixos(memo)
        name_limpo, doc_name = extrair_e_limpar_documentos_e_prefixos(name)

        documento_encontrado = (
            doc_geral or doc_payee or doc_memo or doc_name or None
        )

        if any(termo in texto_completo.upper() for termo in encargos_bancarios):
          favorecido = (
              'Itaú Unibanco S.A.' if 'Itaú' in conta_origem else 'Banco'
          )
          descricao = (
              memo_limpo
              or payee_limpo
              or name_limpo
              or 'Encargo/Tarifa Bancária'
          )
        else:
          favorecido = (
              payee_limpo
              or name_limpo
              or memo_limpo
              or texto_geral_limpo
              or 'Lançamento Bancário'
          )
          descricao = (
              memo_limpo
              if memo_limpo
              else (
                  name_limpo
                  if name_limpo != payee_limpo
                  else 'Movimentação Conta Corrente'
              )
          )

        # PASSO EXTRA DE SEGURANÇA: Limpa diretamente as variáveis finais
        favorecido, _ = extrair_e_limpar_documentos_e_prefixos(favorecido)
        descricao, _ = extrair_e_limpar_documentos_e_prefixos(descricao)

        if not favorecido:
          favorecido = 'Lançamento Bancário'

        if favorecido.upper() == descricao.upper() or not descricao:
          descricao = 'Transação PIX / Bancária'

        hash_string = f'{data}_{tipo}_{valor_absoluto}_{conta_origem}_{tx.id}'
        hash_transacao = hashlib.md5(hash_string.encode('utf-8')).hexdigest()

        existe = LancamentoContabilidade.query.filter_by(
            hash_transacao=hash_transacao
        ).first()

        if not existe:
          novo_item = LancamentoContabilidade(
              data_movimentacao=data,
              numero_documento=numero_doc,
              favorecido=favorecido,
              cpf_cnpj=documento_encontrado,
              descricao=descricao,
              valor=valor_absoluto,
              tipo=tipo,
              conta_origem=conta_origem,
              hash_transacao=hash_transacao,
          )
          db.session.add(novo_item)
          novos_registros += 1
        else:
          duplicados += 1

      db.session.commit()
      flash(
          f'Importação concluída! {novos_registros} novos lançamentos salvos.'
          f' ({duplicados} ignorados por já existirem ou serem saldos)',
          'success',
      )

    except Exception as e:
      db.session.rollback()
      flash(f'Erro ao processar o arquivo OFX: {e}', 'danger')

    return redirect(url_for('financeiro'))

  lancamentos = (
      LancamentoContabilidade.query.order_by(
          LancamentoContabilidade.data_movimentacao.asc()
      )
      .all()
  )
  return render_template('financeiro.html', lancamentos=lancamentos)


@app.route('/financeiro/novo', methods=['POST'])
def novo_lancamento_manual():
  try:
    data_str = request.form.get('data_movimentacao')
    data = (
        datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else None
    )

    tipo = request.form.get('tipo')
    valor_raw = request.form.get('valor', '0')
    valor = float(valor_raw.replace('.', '').replace(',', '.'))

    favorecido = request.form.get('favorecido', 'Não Informado')
    cpf_cnpj = request.form.get('cpf_cnpj', '').strip() or None
    descricao = request.form.get('descricao', 'Lançamento Manual')
    conta_origem = request.form.get('conta_origem', 'Itaú CC')
    numero_doc = request.form.get('numero_documento', 'MANUAL')

    hash_string = f'MANUAL_{data_str}_{tipo}_{valor}_{conta_origem}_{hashlib.md5(descricao.encode()).hexdigest()[:6]}'
    hash_transacao = hashlib.md5(hash_string.encode('utf-8')).hexdigest()

    novo_item = LancamentoContabilidade(
        data_movimentacao=data,
        numero_documento=numero_doc,
        favorecido=favorecido,
        cpf_cnpj=cpf_cnpj,
        descricao=descricao,
        valor=valor,
        tipo=tipo,
        conta_origem=conta_origem,
        hash_transacao=hash_transacao,
    )
    db.session.add(novo_item)
    db.session.commit()
    flash('Lançamento adicionado com sucesso!', 'success')
  except Exception as e:
    db.session.rollback()
    flash(f'Erro ao salvar lançamento manual: {e}', 'danger')

  return redirect(url_for('financeiro'))


@app.route('/financeiro/limpar', methods=['POST'])
def limpar_financeiro():
  try:
    num_deletados = db.session.query(LancamentoContabilidade).delete()
    db.session.commit()
    flash(
        f'Todos os {num_deletados} lançamentos foram excluídos com sucesso.',
        'warning',
    )
  except Exception as e:
    db.session.rollback()
    flash(f'Erro ao limpar os registros: {e}', 'danger')
  return redirect(url_for('financeiro'))


@app.route('/financeiro/exportar', methods=['GET'])
def exportar_financeiro():
  lancamentos = (
      LancamentoContabilidade.query.order_by(
          LancamentoContabilidade.data_movimentacao.asc()
      )
      .all()
  )

  dados = []
  for item in lancamentos:
    data_formatada = ''
    if item.data_movimentacao:
      if hasattr(item.data_movimentacao, 'strftime'):
        data_formatada = item.data_movimentacao.strftime('%d/%m/%Y')
      else:
        data_formatada = str(item.data_movimentacao)

    dados.append({
        'Data': data_formatada,
        'Nº Documento': item.numero_documento or 'S/N',
        'Favorecido / Cliente': item.favorecido or '',
        'CPF / CNPJ': item.cpf_cnpj or '',
        'Descrição': item.descricao or '',
        'Conta Origem': item.conta_origem or '',
        'Tipo': item.tipo or '',
        'Valor (R$)': float(item.valor or 0),
    })

  df = pd.DataFrame(dados)
  output = io.BytesIO()

  with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Extrato Financeiro')
    ws = writer.sheets['Extrato Financeiro']

    font_header = Font(name='Arial', size=11, bold=True, color='FFFFFF')
    fill_header = PatternFill(
        start_color='1A365D', end_color='1A365D', fill_type='solid'
    )
    fill_zebra = PatternFill(
        start_color='F8FAFC', end_color='F8FAFC', fill_type='solid'
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')

    border_light = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0'),
    )

    ws.row_dimensions[1].height = 26
    for col_idx, col_name in enumerate(df.columns, 1):
      cell = ws.cell(row=1, column=col_idx)
      cell.font = font_header
      cell.fill = fill_header
      cell.border = border_light
      cell.alignment = (
          align_center
          if col_name
          in ['Data', 'Nº Documento', 'CPF / CNPJ', 'Tipo', 'Conta Origem']
          else (align_right if 'Valor' in col_name else align_left)
      )

    for row_idx in range(2, len(df) + 2):
      ws.row_dimensions[row_idx].height = 20
      is_even = row_idx % 2 == 0

      for col_idx, col_name in enumerate(df.columns, 1):
        cell = ws.cell(row=row_idx, column=col_idx)
        cell.border = border_light
        if is_even:
          cell.fill = fill_zebra

        if col_name in ['Data', 'Nº Documento', 'CPF / CNPJ', 'Tipo']:
          cell.alignment = align_center
        elif col_name == 'Valor (R$)':
          cell.alignment = align_right
          cell.number_format = 'R$ #,##0.00'

          tipo_val = str(
              ws.cell(
                  row=row_idx, column=df.columns.get_loc('Tipo') + 1
              ).value
          ).upper()
          if 'PAGAMENTO' in tipo_val:
            cell.font = Font(name='Arial', size=10, color='C53030', bold=True)
          else:
            cell.font = Font(name='Arial', size=10, color='276749', bold=True)
        else:
          cell.alignment = align_left

    for col in ws.columns:
      max_len = max(len(str(cell.value or '')) for cell in col)
      col_letter = get_column_letter(col[0].column)
      ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

  output.seek(0)
  return send_file(
      output,
      download_name='Extrato_Financeiro_MJP.xlsx',
      as_attachment=True,
      mimetype=(
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ),
  )