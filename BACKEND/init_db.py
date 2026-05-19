import sqlite3

def atualizar_banco():
    conn = sqlite3.connect('ecotins.db')
    cursor = conn.cursor()
    
    print("Verificando e injetando novas colunas de status no EcoTins...")
    
    # Adiciona a coluna para a data de agendamento da coleta
    try:
        cursor.execute("ALTER TABLE solicitacoes ADD COLUMN data_recolhimento TEXT")
        print("- Coluna 'data_recolhimento' adicionada com sucesso.")
    except sqlite3.OperationalError:
        print("- Coluna 'data_recolhimento' já existia no banco.")

    # Adiciona a coluna para o registro de data e hora em que foi concluída
    try:
        cursor.execute("ALTER TABLE solicitacoes ADD COLUMN data_hora_realizada TEXT")
        print("- Coluna 'data_hora_realizada' adicionada com sucesso.")
    except sqlite3.OperationalError:
        print("- Coluna 'data_hora_realizada' já existia no banco.")

    conn.commit()
    conn.close()
    print("Banco de dados atualizado com sucesso!")

if __name__ == '__main__':
    atualizar_banco()