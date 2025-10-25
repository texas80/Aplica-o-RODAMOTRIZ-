from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import os
from datetime import datetime, date
import platform
import threading

# === ReportLab Imports ===
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError:
    print("⚠️ ReportLab não está instalado. Execute: pip install reportlab")
    exit(1)

app = Flask(__name__)
app.secret_key = 'rodamotriz_secret_key_2024'

class SistemaRodamotriz:
    def __init__(self):
        # Permitir uso da conexão em threads diferentes (Flask pode servir em threads)
        self.conn = sqlite3.connect(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'rodamotriz.db'), check_same_thread=False)
        self.cursor = self.conn.cursor()
        # Lock para serializar acessos ao cursor/commit
        self.lock = threading.Lock()
        self.criar_tabelas()

    def criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados"""
        # Tabela de clientes
        with self.lock:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cnpj_cpf TEXT NOT NULL,
                    endereco TEXT NOT NULL,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabela de máquinas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS maquinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marca TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    ano INTEGER NOT NULL,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabela de registros de trabalho
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS registros_trabalho (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    maquina_id INTEGER NOT NULL,
                    local_trabalho TEXT NOT NULL,
                    data_inicio TEXT NOT NULL, 
                    data_final TEXT NOT NULL,
                    horimetro_inicial REAL NOT NULL,
                    horimetro_final REAL NOT NULL,
                    horas_trabalhadas REAL NOT NULL,
                    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
                )
            ''')

            self.conn.commit()

    def cadastrar_cliente(self, nome, cnpj_cpf, endereco):
        """Cadastra um novo cliente no banco de dados"""
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT INTO clientes (nome, cnpj_cpf, endereco)
                    VALUES (?, ?, ?)
                ''', (nome, cnpj_cpf, endereco))
                self.conn.commit()
                return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Erro de integridade ao cadastrar cliente: {e}")
        except Exception as e:
            raise Exception(f"Erro inesperado ao cadastrar cliente: {e}")

    def listar_clientes(self):
        """Lista todos os clientes cadastrados"""
        with self.lock:
            self.cursor.execute(
                'SELECT id, nome, cnpj_cpf, endereco FROM clientes ORDER BY id')
            return self.cursor.fetchall()

    def cadastrar_maquina(self, marca, modelo, ano):
        """Cadastra uma nova máquina no banco de dados"""
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT INTO maquinas (marca, modelo, ano)
                    VALUES (?, ?, ?)
                ''', (marca, modelo, ano))
                self.conn.commit()
                return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Erro de integridade ao cadastrar máquina: {e}")
        except Exception as e:
            raise Exception(f"Erro inesperado ao cadastrar máquina: {e}")

    def listar_maquinas(self):
        """Lista todas as máquinas cadastradas"""
        with self.lock:
            self.cursor.execute(
                'SELECT id, marca, modelo, ano FROM maquinas ORDER BY id')
            return self.cursor.fetchall()

    def validar_data(self, data_str):
        """Valida e converte data no formato dd/mm/yyyy"""
        try:
            datetime.strptime(data_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    def registrar_trabalho(self, cliente_id, maquina_id, local_trabalho,
                           data_inicio, data_final, horimetro_inicial, horimetro_final):
        """Registra um trabalho realizado"""
        
        # Validação de Horímetro
        if horimetro_final <= horimetro_inicial:
            raise Exception("O horímetro final deve ser maior que o inicial!")

        # Validação de Data
        if not self.validar_data(data_inicio) or not self.validar_data(data_final):
            raise Exception("Data inválida! Use o formato dd/mm/yyyy")

        # Validação de Cliente e Máquina
        with self.lock:
            self.cursor.execute('SELECT 1 FROM clientes WHERE id = ?', (cliente_id,))
            if self.cursor.fetchone() is None:
                raise Exception(f"Cliente com ID {cliente_id} não encontrado.")

            self.cursor.execute('SELECT 1 FROM maquinas WHERE id = ?', (maquina_id,))
            if self.cursor.fetchone() is None:
                raise Exception(f"Máquina com ID {maquina_id} não encontrada.")

        # Cálculo
        horas_trabalhadas = horimetro_final - horimetro_inicial

        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT INTO registros_trabalho 
                    (cliente_id, maquina_id, local_trabalho, data_inicio, data_final,
                     horimetro_inicial, horimetro_final, horas_trabalhadas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (cliente_id, maquina_id, local_trabalho, data_inicio, data_final,
                      horimetro_inicial, horimetro_final, horas_trabalhadas))

                self.conn.commit()
                return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Erro de integridade: {e}")
        except Exception as e:
            raise Exception(f"Erro ao registrar trabalho: {e}")

    def listar_trabalhos(self):
        """Lista todos os registros de trabalho"""
        with self.lock:
            self.cursor.execute('''
                SELECT r.id, c.nome, m.marca, m.modelo, r.local_trabalho, 
                       r.data_inicio, r.data_final, r.horas_trabalhadas, r.data_registro
                FROM registros_trabalho r
                JOIN clientes c ON r.cliente_id = c.id
                JOIN maquinas m ON r.maquina_id = m.id
                ORDER BY r.data_registro DESC
            ''')
            return self.cursor.fetchall()

    def gerar_relatorio_pdf(self, registro_id):
        """Gera relatório em PDF do registro de trabalho"""
        try:
            # Buscar dados do registro
            with self.lock:
                self.cursor.execute('''
                    SELECT r.id, c.nome, c.cnpj_cpf, c.endereco,
                           m.marca, m.modelo, m.ano,
                           r.local_trabalho, r.data_inicio, r.data_final,
                           r.horimetro_inicial, r.horimetro_final, r.horas_trabalhadas,
                           r.data_registro
                    FROM registros_trabalho r
                    JOIN clientes c ON r.cliente_id = c.id
                    JOIN maquinas m ON r.maquina_id = m.id
                    WHERE r.id = ?
                ''', (registro_id,))

                dados = self.cursor.fetchone()

            if not dados:
                raise Exception("Registro não encontrado!")

            # Criar diretório para relatórios se não existir
            caminho_relatorios = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'relatorios')
            if not os.path.exists(caminho_relatorios):
                os.makedirs(caminho_relatorios)

            # Nome do arquivo PDF
            nome_arquivo = f"{caminho_relatorios}/relatorio_{registro_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            # Criar documento PDF
            doc = SimpleDocTemplate(nome_arquivo, pagesize=A4,
                                    rightMargin=cm, leftMargin=cm,
                                    topMargin=cm, bottomMargin=cm)
            elementos = []

            # Estilos
            styles = getSampleStyleSheet()

            # Estilo Título
            estilo_titulo = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#0d47a1'),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )

            # Estilo Subtítulo
            estilo_subtitulo = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#1976d2'),
                spaceAfter=16,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )

            estilo_cabecalho_tabela = ParagraphStyle(
                'CabecalhoTabela',
                parent=styles['Heading3'],
                fontSize=11,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )

            # Cabeçalho
            elementos.append(
                Paragraph("RODAMOTRIZ COM. DE MÁQUINAS E PEÇAS LTDA", estilo_titulo))
            elementos.append(
                Paragraph("RELATÓRIO DE HORA MÁQUINA TRABALHADA", estilo_subtitulo))
            elementos.append(Spacer(1, 0.5*cm))

            # Informações do relatório
            elementos.append(Paragraph(
                f"<b>Relatório Nº:</b> <font color='#c62828'>{dados[0]:05d}</font>", styles['Normal']))
            elementos.append(Paragraph(
                f"<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            elementos.append(Spacer(1, 0.5*cm))

            # Dados do Cliente
            elementos.append(
                Paragraph("DADOS DO CLIENTE", estilo_cabecalho_tabela))
            dados_cliente = [
                ['Nome:', dados[1]],
                ['CNPJ/CPF:', dados[2]],
                ['Endereço:', dados[3]]
            ]

            tabela_cliente = Table(dados_cliente, colWidths=[4*cm, 13*cm])
            tabela_cliente.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elementos.append(tabela_cliente)
            elementos.append(Spacer(1, 0.5*cm))

            # Dados da Máquina
            elementos.append(
                Paragraph("DADOS DA MÁQUINA", estilo_cabecalho_tabela))
            dados_maquina = [
                ['Marca:', dados[4]],
                ['Modelo:', dados[5]],
                ['Ano:', str(dados[6])]
            ]

            tabela_maquina = Table(dados_maquina, colWidths=[4*cm, 13*cm])
            tabela_maquina.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elementos.append(tabela_maquina)
            elementos.append(Spacer(1, 0.5*cm))

            # Dados do Trabalho
            elementos.append(
                Paragraph("DADOS DO TRABALHO", estilo_cabecalho_tabela))
            dados_trabalho = [
                ['Local de Trabalho:', dados[7]],
                ['Data Início:', dados[8]],
                ['Data Final:', dados[9]],
                ['Horímetro Inicial:', f"{dados[10]:.2f} horas"],
                ['Horímetro Final:', f"{dados[11]:.2f} horas"]
            ]

            tabela_trabalho = Table(dados_trabalho, colWidths=[4*cm, 13*cm])
            tabela_trabalho.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elementos.append(tabela_trabalho)
            elementos.append(Spacer(1, 0.8*cm))
            # Verificar horas totais acumuladas para o mesmo modelo de máquina e gerar alarmes
            marca = dados[4]
            modelo = dados[5]
            with self.lock:
                self.cursor.execute('''
                    SELECT SUM(r.horas_trabalhadas)
                    FROM registros_trabalho r
                    JOIN maquinas m ON r.maquina_id = m.id
                    WHERE m.marca = ? AND m.modelo = ?
                ''', (marca, modelo))
                soma = self.cursor.fetchone()

            total_acumulado = float(soma[0]) if soma and soma[0] is not None else float(dados[12])

            # Gerar seção de alarmes (500,1000,1500,2000)
            thresholds = [500, 1000, 1500, 2000]
            alarmes_reached = [t for t in thresholds if total_acumulado >= t]

            elementos.append(Paragraph('ALARMES / MANUTENÇÃO (por modelo)', estilo_cabecalho_tabela))
            alarm_rows = []
            for t in thresholds:
                status = 'ATENDIDO' if t in alarmes_reached else 'PENDENTE'
                alarm_rows.append([f'{t} HORAS', status])

            tabela_alarmes = Table(alarm_rows, colWidths=[11*cm, 6*cm])
            tabela_alarmes.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ]))

            # Destacar em vermelho as linhas atendidas
            for i, t in enumerate(thresholds):
                if t in alarmes_reached:
                    tabela_alarmes.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (0, i), colors.HexColor('#ffebee')),
                        ('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#c62828')),
                        ('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
                    ]))

            elementos.append(tabela_alarmes)
            elementos.append(Spacer(1, 0.6*cm))

            # Total de Horas (exibido abaixo dos alarmes)
            dados_total = [
                ['TOTAL DE HORAS TRABALHADAS (modelo):', f"{total_acumulado:.2f} HORAS"]
            ]

            tabela_total = Table(dados_total, colWidths=[11*cm, 6*cm])
            tabela_total.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
                ('TOPPADDING', (0, 0), (-1, -1), 14),
            ]))
            elementos.append(tabela_total)
            elementos.append(Spacer(1, 1*cm))

            # Rodapé
            elementos.append(Spacer(1, 2*cm))
            assinatura_data = [['', '', '']]
            tabela_assinatura = Table(
                assinatura_data, colWidths=[6*cm, 5*cm, 6*cm])
            tabela_assinatura.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
            ]))
            elementos.append(tabela_assinatura)

            elementos.append(Paragraph(
                "Assinatura Autorizada (Rodamotriz)",
                ParagraphStyle(
                    'Left', parent=styles['Normal'], alignment=TA_CENTER, spaceBefore=0)
            ))

            # Construir PDF
            doc.build(elementos)
            return nome_arquivo

        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {e}")

    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        # Fechar com proteção de lock
        try:
            with self.lock:
                self.conn.close()
        except Exception:
            # Se não for possível obter o lock, tentar fechar de qualquer forma
            try:
                self.conn.close()
            except Exception:
                pass

# Inicializar sistema
sistema = SistemaRodamotriz()

# === ROTAS FLASK ===

@app.route('/')
def index():
    """Página inicial"""
    # Buscar estatísticas
    clientes_count = len(sistema.listar_clientes())
    maquinas_count = len(sistema.listar_maquinas())
    trabalhos = sistema.listar_trabalhos()
    trabalhos_count = len(trabalhos)
    
    # Calcular horas totais
    horas_totais = sum(trabalho[7] for trabalho in trabalhos) if trabalhos else 0
    
    return render_template('index.html', 
                         clientes_count=clientes_count,
                         maquinas_count=maquinas_count,
                         trabalhos_count=trabalhos_count,
                         horas_totais=f"{horas_totais:.1f}")

@app.route('/clientes')
def clientes():
    """Lista de clientes"""
    clientes = sistema.listar_clientes()
    return render_template('clientes.html', clientes=clientes)

# Rota para deletar cliente
@app.route('/deletar_cliente/<int:cliente_id>', methods=['POST'])
def deletar_cliente(cliente_id):
    try:
        with sistema.lock:
            sistema.cursor.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
            sistema.conn.commit()
        flash(f'Cliente {cliente_id} removido com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao remover cliente: {e}', 'error')
    return redirect(url_for('clientes'))

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    """Cadastro de cliente"""
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            cnpj_cpf = request.form['cnpj_cpf']
            endereco = request.form['endereco']
            
            if not nome or not cnpj_cpf or not endereco:
                flash('Todos os campos são obrigatórios!', 'error')
            else:
                sistema.cadastrar_cliente(nome, cnpj_cpf, endereco)
                flash('Cliente cadastrado com sucesso!', 'success')
                return redirect(url_for('clientes'))
        except Exception as e:
            flash(f'Erro ao cadastrar cliente: {str(e)}', 'error')
    
    return render_template('cadastrar_cliente.html')

@app.route('/maquinas')
def maquinas():
    """Lista de máquinas"""
    maquinas = sistema.listar_maquinas()
    return render_template('maquinas.html', maquinas=maquinas)

# Rota para deletar máquina
@app.route('/deletar_maquina/<int:maquina_id>', methods=['POST'])
def deletar_maquina(maquina_id):
    try:
        with sistema.lock:
            sistema.cursor.execute('DELETE FROM maquinas WHERE id = ?', (maquina_id,))
            sistema.conn.commit()
        flash(f'Máquina {maquina_id} removida com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao remover máquina: {e}', 'error')
    return redirect(url_for('maquinas'))

@app.route('/cadastrar_maquina', methods=['GET', 'POST'])
def cadastrar_maquina():
    """Cadastro de máquina"""
    if request.method == 'POST':
        try:
            marca = request.form['marca']
            modelo = request.form['modelo']
            ano = int(request.form['ano'])
            
            if not marca or not modelo:
                flash('Todos os campos são obrigatórios!', 'error')
            elif ano < 1900 or ano > date.today().year + 1:
                flash('Ano inválido!', 'error')
            else:
                sistema.cadastrar_maquina(marca, modelo, ano)
                flash('Máquina cadastrada com sucesso!', 'success')
                return redirect(url_for('maquinas'))
        except ValueError:
            flash('Ano deve ser um número!', 'error')
        except Exception as e:
            flash(f'Erro ao cadastrar máquina: {str(e)}', 'error')
    
    # Fornecer o ano atual ao template para renderizar o campo 'max' corretamente
    return render_template('cadastrar_maquina.html', ano_atual=date.today().year)

@app.route('/trabalhos')
def trabalhos():
    """Lista de trabalhos"""
    trabalhos = sistema.listar_trabalhos()
    return render_template('trabalhos.html', trabalhos=trabalhos)

@app.route('/registrar_trabalho', methods=['GET', 'POST'])
def registrar_trabalho():
    """Registro de trabalho"""
    if request.method == 'POST':
        try:
            cliente_id = int(request.form['cliente_id'])
            maquina_id = int(request.form['maquina_id'])
            local_trabalho = request.form['local_trabalho']
            data_inicio = request.form['data_inicio']
            data_final = request.form['data_final']
            horimetro_inicial = float(request.form['horimetro_inicial'])
            horimetro_final = float(request.form['horimetro_final'])
            
            registro_id = sistema.registrar_trabalho(
                cliente_id, maquina_id, local_trabalho,
                data_inicio, data_final, horimetro_inicial, horimetro_final
            )
            
            flash(f'Trabalho registrado com sucesso! ID: {registro_id}', 'success')
            return redirect(url_for('trabalhos'))
            
        except ValueError:
            flash('Valores inválidos! Verifique os dados inseridos.', 'error')
        except Exception as e:
            flash(f'Erro ao registrar trabalho: {str(e)}', 'error')
    
    # Buscar clientes e máquinas para o formulário
    clientes = sistema.listar_clientes()
    maquinas = sistema.listar_maquinas()
    return render_template('registrar_trabalho.html', clientes=clientes, maquinas=maquinas)

@app.route('/gerar_pdf/<int:registro_id>')
def gerar_pdf(registro_id):
    """Gera PDF do registro"""
    try:
        arquivo_pdf = sistema.gerar_relatorio_pdf(registro_id)
        return send_file(arquivo_pdf, as_attachment=True, 
                       download_name=f'relatorio_{registro_id}.pdf')
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('trabalhos'))

# Nova rota para deletar relatório PDF
@app.route('/deletar_relatorio/<int:registro_id>', methods=['POST'])
def deletar_relatorio(registro_id):
    """Deleta o arquivo PDF gerado para o registro informado"""
    import glob
    import os
    caminho_relatorios = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'relatorios')
    # Busca todos arquivos de relatório para o registro
    padrao = os.path.join(caminho_relatorios, f'relatorio_{registro_id}_*.pdf')
    arquivos = glob.glob(padrao)
    if not arquivos:
        flash(f'Nenhum relatório PDF encontrado para o registro {registro_id}.', 'error')
    else:
        deletados = 0
        for arq in arquivos:
            try:
                os.remove(arq)
                deletados += 1
            except Exception as e:
                flash(f'Erro ao deletar {arq}: {e}', 'error')
        flash(f'{deletados} relatório(s) PDF deletado(s) para o registro {registro_id}.', 'success')

    # Remover o registro de trabalho do banco de dados
    try:
        with sistema.lock:
            sistema.cursor.execute('DELETE FROM registros_trabalho WHERE id = ?', (registro_id,))
            sistema.conn.commit()
        flash(f'Registro de trabalho {registro_id} removido do sistema.', 'success')
    except Exception as e:
        flash(f'Erro ao remover registro do banco: {e}', 'error')

    return redirect(url_for('trabalhos'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
