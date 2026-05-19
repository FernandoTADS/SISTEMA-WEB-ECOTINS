import sqlite3

def resetar_sistema():
    conn = sqlite3.connect('ecotins.db')
    cursor = conn.cursor()
    
    print("Apagando tabelas antigas...")
    cursor.execute('DROP TABLE IF EXISTS solicitacoes;')
    cursor.execute('DROP TABLE IF EXISTS usuarios;')
    
    print("Criando tabela 'usuarios' atualizada...")
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            status TEXT
        );
    ''')
    
    print("Criando tabela 'solicitacoes' atualizada...")
    cursor.execute('''
        CREATE TABLE solicitacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            endereco TEXT,
            tipo_residuo TEXT,
            descricao TEXT,
            status TEXT,
            data_pedido TEXT,
            data_recolhimento TEXT,
            data_hora_realizada TEXT,
            data_exclusao TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        );
    ''')
    
    print("Injetando a conta do Administrador padrão...")
    cursor.execute('''
        INSERT INTO usuarios (nome, email, telefone, senha, tipo, status)
        VALUES ('Administrador EcoTins', 'admin@ecotins.com', '(63) 99999-9999', 'admin123', 'admin', 'Ativo');
    ''')
    
    conn.commit()
    conn.close()
    print("✨ Banco de dados resetado com sucesso total!")

if __name__ == '__main__':
    resetar_sistema()