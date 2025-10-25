# Rodamotriz - Sistema Web de Controle de Horas

Sistema web moderno para controle de horas de máquinas da Rodamotriz Com. de Máquinas e Peças Ltda.

## 🚀 Funcionalidades

- **Gestão de Clientes**: Cadastro e listagem de clientes
- **Gestão de Máquinas**: Cadastro e listagem de máquinas
- **Registro de Trabalhos**: Controle de horas trabalhadas
- **Relatórios PDF**: Geração automática de relatórios em PDF
- **Interface Moderna**: Design responsivo com Bootstrap 5
- **Dashboard**: Estatísticas em tempo real

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

1. **Clone ou baixe os arquivos do projeto**

2. **Instale as dependências:**
   ```bash
   pip install -r requirements_web.txt
   ```

3. **Execute a aplicação:**
   ```bash
   python app_web.py
   ```

4. **Acesse no navegador:**
   ```
   http://localhost:5000
   ```

## 📁 Estrutura do Projeto

```
APP RODA/
├── app_web.py              # Aplicação Flask principal
├── requirements_web.txt    # Dependências da aplicação web
├── rodamotriz.db          # Banco de dados SQLite
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página inicial
│   ├── clientes.html     # Lista de clientes
│   ├── cadastrar_cliente.html
│   ├── maquinas.html     # Lista de máquinas
│   ├── cadastrar_maquina.html
│   ├── trabalhos.html    # Lista de trabalhos
│   └── registrar_trabalho.html
└── relatorios/           # Pasta para PDFs gerados
```

## 🎯 Como Usar

### 1. Cadastrar Cliente
- Acesse "Clientes" no menu
- Clique em "Novo Cliente"
- Preencha os dados e salve

### 2. Cadastrar Máquina
- Acesse "Máquinas" no menu
- Clique em "Nova Máquina"
- Preencha marca, modelo e ano

### 3. Registrar Trabalho
- Acesse "Trabalhos" no menu
- Clique em "Novo Trabalho"
- Selecione cliente e máquina
- Preencha local, datas e horímetros
- O sistema calcula automaticamente as horas trabalhadas

### 4. Gerar Relatório PDF
- Na lista de trabalhos, clique no ícone PDF
- O relatório será baixado automaticamente

## 🔧 Configuração

### Porta e Host
Para alterar a porta ou host, edite o final do arquivo `app_web.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Banco de Dados
O sistema usa SQLite e cria automaticamente o arquivo `rodamotriz.db` na primeira execução.

## 📊 Recursos da Interface

- **Design Responsivo**: Funciona em desktop, tablet e mobile
- **Navegação Intuitiva**: Menu lateral com todas as funcionalidades
- **Feedback Visual**: Mensagens de sucesso e erro
- **Validação de Dados**: Campos obrigatórios e formatos corretos
- **Estatísticas**: Dashboard com contadores em tempo real

## 🚨 Solução de Problemas

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements_web.txt
```

### Erro de Porta em Uso
Altere a porta no arquivo `app_web.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Problemas com PDF
Certifique-se de que o ReportLab está instalado:
```bash
pip install reportlab
```

## 📝 Notas Importantes

- O sistema mantém compatibilidade com o banco de dados da versão desktop
- Os relatórios PDF são salvos na pasta `relatorios/`
- O sistema é totalmente funcional offline
- Todos os dados são armazenados localmente no SQLite

## 🎨 Personalização

Para personalizar o visual:
1. Edite o arquivo `templates/base.html`
2. Modifique as classes CSS no `<style>` do template base
3. Adicione seus próprios estilos

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se todas as dependências estão instaladas
2. Se a porta 5000 está livre
3. Se o Python está na versão correta
4. Se os arquivos de template estão na pasta `templates/`

---

**Rodamotriz Com. de Máquinas e Peças Ltda**  
Sistema de Controle de Horas - Versão Web
