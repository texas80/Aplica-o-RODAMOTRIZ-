#!/usr/bin/env python3
"""
Script de inicialização da aplicação web Rodamotriz
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import reportlab
        print("✅ Todas as dependências estão instaladas!")
        return True
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("📦 Instalando dependências...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"])
            print("✅ Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências. Execute manualmente:")
            print("pip install -r requirements_web.txt")
            return False

def criar_diretorios():
    """Cria diretórios necessários"""
    diretorios = ['templates', 'relatorios']
    for diretorio in diretorios:
        Path(diretorio).mkdir(exist_ok=True)
    print("✅ Diretórios criados/verificados!")

def iniciar_aplicacao():
    """Inicia a aplicação Flask"""
    print("\n🚀 Iniciando aplicação web Rodamotriz...")
    print("📱 A aplicação será aberta automaticamente no navegador")
    print("🌐 URL: http://localhost:5000")
    print("⏹️  Para parar a aplicação, pressione Ctrl+C")
    print("\n" + "="*60)
    
    # Abrir navegador após 2 segundos
    import threading
    import time
    
    def abrir_navegador():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Iniciar Flask
    try:
        from app_web import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar aplicação: {e}")

def main():
    """Função principal"""
    print("🏭 RODAMOTRIZ - Sistema Web de Controle de Horas")
    print("="*60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('app_web.py'):
        print("❌ Arquivo app_web.py não encontrado!")
        print("📁 Certifique-se de estar no diretório correto do projeto")
        return
    
    # Verificar e instalar dependências
    if not verificar_dependencias():
        return
    
    # Criar diretórios necessários
    criar_diretorios()
    
    # Iniciar aplicação
    iniciar_aplicacao()

if __name__ == "__main__":
    main()
