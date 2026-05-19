# EcoTins - Sistema Web de Coleta de Resíduos

Sistema web desenvolvido para gerenciamento de solicitações de coleta de resíduos recicláveis, criado para projeto acadêmico do curso de Tecnologia em Análise e Desenvolvimento de Sistemas (TADS).

---

# Objetivo do Sistema

O EcoTins tem como objetivo facilitar o gerenciamento de:

- Solicitações de coleta de resíduos
- Cadastro de usuários
- Controle administrativo
- Acompanhamento das solicitações
- Organização de resíduos recicláveis

---

# Tecnologias Utilizadas

## Backend

- Python
- Flask
- SQLite

## Frontend

- HTML5
- CSS3
- JavaScript

---

# Estrutura do Projeto

```txt
SISTEMA_WEB_ECOTINS/
│
├── BACKEND/
│   ├── app.py
│   ├── init_db.py
│   ├── requirements.txt
│   ├── ecotins.db
│   ├── reset_db.py
│
├── WEB/
│   ├── admin.html
│   ├── admin_editar_usuario.html
│   ├── admin_excluidas.html
│   ├── admin_usuarios.html
│   ├── admin_status_coleta.html
│   ├── cadastro.html
│   ├── index.html
│   ├── login.css
│   ├── login.html
│   ├── pontosdecoleta.html
│   ├── solicitacoes.html
│   ├── solicitar.html
│   ├── style.css

└── README.md
 
```

---

# Como Executar o Sistema

## 1. Instalar o Python

Download oficial:

https://www.python.org/downloads/

Aconselhável utilizar a versão Python 3.12 por maior compatibilidade.

---

## 2. Abrir o Terminal na Pasta BACKEND

Caso o terminal esteja na pasta raiz do sistema:

```bash
cd BACKEND
```

---

## 3. Instalar as Dependências

Instale todas as bibliotecas necessárias utilizando:

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` instala automaticamente:

- Flask
- Flask Login
- Flask SQLAlchemy

Caso queira instalar manualmente:

```bash
pip install flask
pip install flask-login
pip install flask-sqlalchemy
```

---

# Inicializar o Banco de Dados

Ainda dentro da pasta BACKEND execute:

```bash
python init_db.py
```

Esse comando irá:

- Criar o banco SQLite
- Criar as tabelas do sistema
- Criar o usuário administrador padrão

---

# IMPORTANTE

O terminal PRECISA estar dentro da pasta `BACKEND` antes de executar:

```bash
python init_db.py
```

Exemplo correto:

```bash
cd BACKEND
python init_db.py
```

Caso contrário, o SQLite pode criar o banco de dados na pasta errada, causando erros como:

```txt
sqlite3.OperationalError: no such table: usuarios
```

---

# Executar o Sistema

Ainda dentro da pasta BACKEND execute:

```bash
python app.py
```

---

# Acesso ao Sistema

Após executar o sistema, abra no navegador:

```txt
http://127.0.0.1:5000
```

---

# Usuário Administrador

O sistema cria automaticamente um administrador padrão.

## Login

```txt
admin@ecotins.com
```

## Senha

```txt
admin123
```

---

# Funcionalidades do Sistema

## Usuário Comum

- Cadastro
- Login
- Solicitar coleta
- Visualizar solicitações
- Excluir solicitações

## Administrador

- Visualizar usuários
- Editar usuários
- Excluir usuários
- Visualizar solicitações
- Painel administrativo

---

# Banco de Dados

O sistema utiliza SQLite.

Arquivo:

```txt
ecotins.db
```

Tabelas:

- usuarios
- solicitacoes
- solicitacoes_excluidas

---

# Sistema de Sessão

O sistema utiliza sessão Flask para:

- Controle de login
- Controle administrativo
- Proteção de páginas

---

# Melhorias Futuras

- Upload de imagens
- Integração com mapas
- API REST
- Dashboard com gráficos
- Responsividade mobile
- Criptografia de senhas
- Deploy em nuvem

---

# Desenvolvido por

Projeto acadêmico desenvolvido pelos discentes ELISEU TAVARES DE LIMA, FERNANDO SILVA MACEDO, GERÓNIMO MARTÍN CAMPANELLO e LUANE ANTUNES BORGES DOS SANTOS
para o curso de Tecnologia em Análise e Desenvolvimento de Sistemas (TADS), no seminário tech 2026-1.

---

# Licença

Projeto acadêmico para fins educacionais.
