import sqlite3
import os
import sys
from datetime import datetime, date  # Importando date também
import platform  # Já estava sendo importado, mas movido para os imports gerais

# === ReportLab Imports (Sem alterações na versão, pois é a padrão e consolidada) ===
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError:
    print("⚠️ ReportLab não está instalado. Execute: pip install reportlab")
    sys.exit(1)

# Para o atalho no Windows, se você não tem certeza que a biblioteca win32com.client está instalada,
# é melhor mantê-la como um import local dentro de 'criar_atalho_desktop'


class SistemaRodamotriz:
    def __init__(self):
        # Usando 'rodamotriz.db' no diretório do script
        self.conn = sqlite3.connect(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'rodamotriz.db'))
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados"""
        # Tabela de clientes
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
        # data_inicio e data_final são TEXT no formato 'dd/mm/yyyy'
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
            self.cursor.execute('''
                INSERT INTO clientes (nome, cnpj_cpf, endereco)
                VALUES (?, ?, ?)
            ''', (nome, cnpj_cpf, endereco))
            self.conn.commit()
            print(
                f"\n✅ Cliente cadastrado com sucesso! ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(
                f"\n❌ Erro de integridade ao cadastrar cliente (dados duplicados ou faltantes): {e}")
            return None
        except Exception as e:
            print(f"\n❌ Erro inesperado ao cadastrar cliente: {e}")
            return None

    def listar_clientes(self):
        """Lista todos os clientes cadastrados"""
        self.cursor.execute(
            'SELECT id, nome, cnpj_cpf, endereco FROM clientes ORDER BY id')
        clientes = self.cursor.fetchall()

        if not clientes:
            print("\n⚠️ Nenhum cliente cadastrado.")
            return []

        # Debug: mostrar dados brutos
        print(f"\n🔍 DEBUG - Dados brutos do banco:")
        for i, cliente in enumerate(clientes):
            print(f"Cliente {i+1}: {cliente}")

        print("\n" + "="*120)
        print("CLIENTES CADASTRADOS".center(120))
        print("="*120)
        print(f"{'ID':<5} {'NOME':<35} {'CNPJ/CPF':<25} {'ENDEREÇO':<50}")
        print("-"*120)

        for cliente in clientes:
            # Garantir que os dados não sejam None
            id_cliente = cliente[0] if cliente[0] is not None else "N/A"
            nome = cliente[1] if cliente[1] is not None else "N/A"
            cnpj_cpf = cliente[2] if cliente[2] is not None else "N/A"
            endereco = cliente[3] if cliente[3] is not None else "N/A"

            # Truncar strings muito longas para exibição
            nome_display = nome[:32] + "..." if len(nome) > 35 else nome
            cnpj_cpf_display = cnpj_cpf[:22] + \
                "..." if len(cnpj_cpf) > 25 else cnpj_cpf
            endereco_display = endereco[:47] + \
                "..." if len(endereco) > 50 else endereco

            print(
                f"{id_cliente:<5} {nome_display:<35} {cnpj_cpf_display:<25} {endereco_display:<50}")

        print("="*120)
        return clientes

    def cadastrar_maquina(self, marca, modelo, ano):
        """Cadastra uma nova máquina no banco de dados"""
        try:
            self.cursor.execute('''
                INSERT INTO maquinas (marca, modelo, ano)
                VALUES (?, ?, ?)
            ''', (marca, modelo, ano))
            self.conn.commit()
            print(
                f"\n✅ Máquina cadastrada com sucesso! ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(
                f"\n❌ Erro de integridade ao cadastrar máquina (dados duplicados ou faltantes): {e}")
            return None
        except Exception as e:
            print(f"\n❌ Erro inesperado ao cadastrar máquina: {e}")
            return None

    def listar_maquinas(self):
        """Lista todas as máquinas cadastradas"""
        self.cursor.execute(
            'SELECT id, marca, modelo, ano FROM maquinas ORDER BY id')
        maquinas = self.cursor.fetchall()

        if not maquinas:
            print("\n⚠️ Nenhuma máquina cadastrada.")
            return []

        print("\n" + "="*100)
        print("MÁQUINAS CADASTRADAS".center(100))
        print("="*100)
        print(f"{'ID':<5} {'MARCA':<30} {'MODELO':<40} {'ANO':<10}")
        print("-"*100)

        for maquina in maquinas:
            # Garantir que os dados não sejam None
            id_maquina = maquina[0] if maquina[0] is not None else "N/A"
            marca = maquina[1] if maquina[1] is not None else "N/A"
            modelo = maquina[2] if maquina[2] is not None else "N/A"
            ano = maquina[3] if maquina[3] is not None else "N/A"

            # Truncar strings muito longas para exibição
            marca_display = marca[:27] + "..." if len(marca) > 30 else marca
            modelo_display = modelo[:37] + \
                "..." if len(modelo) > 40 else modelo

            print(
                f"{id_maquina:<5} {marca_display:<30} {modelo_display:<40} {ano:<10}")

        print("="*100)
        return maquinas

    def validar_data(self, data_str):
        """Valida e converte data no formato dd/mm/yyyy"""
        # CORREÇÃO: Usando %Y (ano com 4 dígitos) para robustez
        try:
            datetime.strptime(data_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    def registrar_trabalho(self, cliente_id, maquina_id, local_trabalho,
                           data_inicio, data_final, horimetro_inicial, horimetro_final):
        """Registra um trabalho realizado"""

        # 1. Validação de Horímetro
        if horimetro_final <= horimetro_inicial:
            print("\n❌ Erro: O horímetro final deve ser **maior** que o inicial!")
            return None

        # 2. Validação de Data (formato dd/mm/yyyy)
        if not self.validar_data(data_inicio) or not self.validar_data(data_final):
            print("\n❌ Erro: Data inválida! Use o formato **dd/mm/yyyy**")
            return None

        # 3. Validação de Cliente e Máquina (melhoria)
        self.cursor.execute(
            'SELECT 1 FROM clientes WHERE id = ?', (cliente_id,))
        if self.cursor.fetchone() is None:
            print(f"\n❌ Erro: Cliente com ID **{cliente_id}** não encontrado.")
            return None

        self.cursor.execute(
            'SELECT 1 FROM maquinas WHERE id = ?', (maquina_id,))
        if self.cursor.fetchone() is None:
            print(f"\n❌ Erro: Máquina com ID **{maquina_id}** não encontrada.")
            return None

        # Cálculo
        horas_trabalhadas = horimetro_final - horimetro_inicial

        try:
            self.cursor.execute('''
                INSERT INTO registros_trabalho 
                (cliente_id, maquina_id, local_trabalho, data_inicio, data_final,
                 horimetro_inicial, horimetro_final, horas_trabalhadas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cliente_id, maquina_id, local_trabalho, data_inicio, data_final,
                  horimetro_inicial, horimetro_final, horas_trabalhadas))

            self.conn.commit()

            print("\n" + "="*80)
            print("REGISTRO DE TRABALHO CONCLUÍDO".center(80))
            print("="*80)
            print(f"Local de Trabalho:      {local_trabalho}")
            print(f"Período:                {data_inicio} a {data_final}")
            print(f"Horímetro Inicial:      {horimetro_inicial:.2f} horas")
            print(f"Horímetro Final:        {horimetro_final:.2f} horas")
            print(f"**Horas Trabalhadas:** **{horas_trabalhadas:.2f} horas**")
            print("="*80)

            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(
                f"\n❌ Erro de integridade (Verifique se cliente/máquina existem): {e}")
            return None
        except Exception as e:
            print(f"\n❌ Erro ao registrar trabalho: {e}")
            return None

    def gerar_relatorio_pdf(self, registro_id):
        """Gera relatório em PDF do registro de trabalho"""
        try:
            # Buscar dados do registro
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
                print("\n❌ Registro não encontrado!")
                return None

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

            # Estilo Título (melhoria na cor)
            estilo_titulo = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#0d47a1'),  # Azul mais escuro
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

            tabela_cliente = Table(dados_cliente, colWidths=[
                                   4*cm, 13*cm])  # Ajuste na largura
            tabela_cliente.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Reduzido padding
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

            tabela_maquina = Table(dados_maquina, colWidths=[
                                   4*cm, 13*cm])  # Ajuste na largura
            tabela_maquina.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Reduzido padding
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
                # A última linha vazia foi removida, pois não é necessária
            ]

            tabela_trabalho = Table(dados_trabalho, colWidths=[
                                    4*cm, 13*cm])  # Ajuste na largura
            tabela_trabalho.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Reduzido padding
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elementos.append(tabela_trabalho)
            elementos.append(Spacer(1, 0.8*cm))

            # Total de Horas (Destaque)
            dados_total = [
                ['TOTAL DE HORAS TRABALHADAS:', f"{dados[12]:.2f} HORAS"]
            ]

            tabela_total = Table(dados_total, colWidths=[
                                 11*cm, 6*cm])  # Ajuste na largura
            tabela_total.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),  # Aumentado fonte
                ('BOTTOMPADDING', (0, 0), (-1, -1), 14),  # Aumentado padding
                ('TOPPADDING', (0, 0), (-1, -1), 14),
            ]))
            elementos.append(tabela_total)
            elementos.append(Spacer(1, 1*cm))

            # Rodapé (Assinatura)
            elementos.append(Spacer(1, 2*cm))

            # Linha da assinatura (centralizada manualmente por espacamento)
            assinatura_data = [
                ['', '', '']
            ]
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

            # Texto da assinatura
            elementos.append(Paragraph(
                "Assinatura Autorizada (Rodamotriz)",
                ParagraphStyle(
                    'Left', parent=styles['Normal'], alignment=TA_CENTER, spaceBefore=0)
            ))

            # Construir PDF
            doc.build(elementos)

            print(f"\n✅ Relatório gerado com sucesso!")
            print(f"📄 Arquivo: {os.path.abspath(nome_arquivo)}")

            return nome_arquivo

        except Exception as e:
            print(f"\n❌ Erro ao gerar relatório: {e}")
            # Mantido o traceback para debug em caso de erro no PDF
            import traceback
            traceback.print_exc()
            return None

    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        self.conn.close()


def criar_atalho_desktop():
    """Cria atalho na área de trabalho"""
    try:
        sistema = platform.system()

        if sistema == "Windows":
            # Importa a biblioteca específica do Windows apenas se for necessário
            try:
                import win32com.client
            except ImportError:
                print(
                    "\n⚠️ A biblioteca 'pywin32' é necessária para criar o atalho no Windows.")
                print("Execute: pip install pywin32")
                return

            desktop = os.path.join(os.path.join(
                os.environ['USERPROFILE']), 'Desktop')
            caminho_script = os.path.abspath(__file__)
            caminho_atalho = os.path.join(desktop, 'HORA MAQUINA.lnk')

            shell = win32com.client.Dispatch("WScript.Shell")
            atalho = shell.CreateShortCut(caminho_atalho)
            atalho.Targetpath = sys.executable
            atalho.Arguments = f'"{caminho_script}"'
            atalho.WorkingDirectory = os.path.dirname(caminho_script)
            atalho.IconLocation = sys.executable
            atalho.save()

            print("\n✅ Atalho criado na área de trabalho!")

        elif sistema == "Linux":
            desktop = os.path.expanduser("~/Desktop")
            caminho_script = os.path.abspath(__file__)
            caminho_atalho = os.path.join(desktop, 'HORA_MAQUINA.desktop')

            # Usando python3 para compatibilidade em distribuições Linux
            conteudo = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=HORA MAQUINA
Comment=Sistema de Controle de Horas de Máquinas
Exec=python3 "{caminho_script}"
Icon=utilities-terminal
Terminal=true
Categories=Application;
"""

            with open(caminho_atalho, 'w') as f:
                f.write(conteudo)

            os.chmod(caminho_atalho, 0o755)
            print("\n✅ Atalho criado na área de trabalho!")

        else:
            print("\n⚠️ Sistema operacional não suportado para criação de atalho.")

    except Exception as e:
        print(
            f"\n⚠️ Não foi possível criar o atalho. Tente executar como administrador ou instale dependências. Erro: {e}")
        print("Execute o programa manualmente.")


def limpar_tela():
    """Limpa a tela do terminal"""
    # Adicionando um fallback se o sistema.os não for 'nt' (Windows) ou 'posix' (Linux/Mac)
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_principal():
    """Exibe o menu principal"""
    print("\n" + "="*80)
    print("RODAMOTRIZ COM. DE MÁQUINAS E PEÇAS LTDA".center(80))
    print("HORA MÁQUINA TRABALHADA".center(80))
    print("="*80)
    print("1 - Cadastrar Cliente")
    print("2 - Listar Clientes")
    print("3 - Cadastrar Máquina")
    print("4 - Listar Máquinas")
    print("5 - Registrar Trabalho")
    print("6 - Gerar Relatório PDF")
    print("7 - Criar Atalho na Área de Trabalho")
    print("8 - Sair")
    print("="*80)


def main():
    sistema = SistemaRodamotriz()

    while True:
        limpar_tela()  # Limpa a tela a cada iteração do loop
        menu_principal()
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            print("\n" + "-"*80)
            print("CADASTRO DE CLIENTE".center(80))
            print("-"*80)

            nome = input("Nome: ").strip()
            cnpj_cpf = input("CNPJ/CPF: ").strip()
            endereco = input("Endereço: ").strip()

            if nome and cnpj_cpf and endereco:
                sistema.cadastrar_cliente(nome, cnpj_cpf, endereco)
            else:
                print("\n❌ Todos os campos são obrigatórios!")

            input("\nPressione ENTER para continuar...")

        elif opcao == '2':
            sistema.listar_clientes()
            input("\nPressione ENTER para continuar...")

        elif opcao == '3':
            print("\n" + "-"*80)
            print("CADASTRO DE MÁQUINA".center(80))
            print("-"*80)

            marca = input("Marca: ").strip()
            modelo = input("Modelo: ").strip()

            try:
                # CORREÇÃO: Usando o ano atual como limite para validação
                ano_atual = date.today().year
                ano = int(input(f"Ano (entre 1900 e {ano_atual+1}): ").strip())
                if ano < 1900 or ano > ano_atual + 1:
                    print("\n❌ Ano inválido!")
                    input("\nPressione ENTER para continuar...")
                    continue
            except ValueError:
                print("\n❌ Ano deve ser um número!")
                input("\nPressione ENTER para continuar...")
                continue

            if marca and modelo:
                sistema.cadastrar_maquina(marca, modelo, ano)
            else:
                print("\n❌ Todos os campos são obrigatórios!")

            input("\nPressione ENTER para continuar...")

        elif opcao == '4':
            sistema.listar_maquinas()
            input("\nPressione ENTER para continuar...")

        elif opcao == '5':
            print("\n" + "-"*80)
            print("REGISTRO DE TRABALHO".center(80))
            print("-"*80)

            # Selecionar cliente
            clientes = sistema.listar_clientes()
            if not clientes:
                input("\nPressione ENTER para continuar...")
                continue

            try:
                cliente_id = int(input("\nDigite o ID do cliente: ").strip())
            except ValueError:
                print("\n❌ ID de Cliente inválido!")
                input("\nPressione ENTER para continuar...")
                continue

            # Selecionar máquina
            maquinas = sistema.listar_maquinas()
            if not maquinas:
                input("\nPressione ENTER para continuar...")
                continue

            try:
                maquina_id = int(input("\nDigite o ID da máquina: ").strip())
            except ValueError:
                print("\n❌ ID de Máquina inválido!")
                input("\nPressione ENTER para continuar...")
                continue

            # Dados do trabalho
            local_trabalho = input("\nLocal de Trabalho: ").strip()
            # CORREÇÃO: Pedindo ano com 4 dígitos
            data_inicio = input("Data Início (dd/mm/yyyy): ").strip()
            data_final = input("Data Final (dd/mm/yyyy): ").strip()

            try:
                horimetro_inicial = float(
                    input("Horímetro Inicial (horas): ").replace(',', '.').strip())
                horimetro_final = float(
                    input("Horímetro Final (horas): ").replace(',', '.').strip())

                registro_id = sistema.registrar_trabalho(
                    cliente_id, maquina_id, local_trabalho,
                    data_inicio, data_final, horimetro_inicial, horimetro_final
                )

                if registro_id:
                    gerar = input(
                        "\nDeseja gerar o relatório PDF agora? (s/n): ").strip().lower()
                    if gerar == 's':
                        sistema.gerar_relatorio_pdf(registro_id)

            except ValueError:
                print("\n❌ Valores inválidos! Digite apenas números para horímetro.")

            input("\nPressione ENTER para continuar...")

        elif opcao == '6':
            try:
                registro_id = int(
                    input("\nDigite o ID do registro para gerar o PDF: ").strip())
                sistema.gerar_relatorio_pdf(registro_id)
            except ValueError:
                print("\n❌ ID inválido!")

            input("\nPressione ENTER para continuar...")

        elif opcao == '7':
            criar_atalho_desktop()
            input("\nPressione ENTER para continuar...")

        elif opcao == '8':
            print("\n👋 Encerrando sistema...")
            sistema.fechar()
            break

        else:
            print("\n❌ Opção inválida!")
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
