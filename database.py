import sqlite3

def iniciar_db():
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    # Criamos a tabela se ela não existir
    # Usamos o link como chave única para evitar duplicatas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ofertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco TEXT,
            link_original TEXT UNIQUE,
            link_afiliado TEXT,
            data_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            enviado_whatsapp BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def salvar_oferta(nome, preco, link):
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO ofertas (nome, preco, link_original)
            VALUES (?, ?, ?)
        ''', (nome, preco, link))
        conn.commit()
        return True # Nova oferta salva
    except sqlite3.IntegrityError:
        return False # Oferta já existia (link duplicado)
    finally:
        conn.close()

def buscar_ofertas_nao_convertidas():
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    # Busca ofertas onde o link_afiliado ainda é nulo
    cursor.execute('SELECT id, link_original FROM ofertas WHERE link_afiliado IS NULL')
    ofertas = cursor.fetchall()
    conn.close()
    return ofertas

def atualizar_link_afiliado(id_oferta, link_convertido):
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE ofertas 
        SET link_afiliado = ? 
        WHERE id = ?
    ''', (link_convertido, id_oferta))
    conn.commit()
    conn.close()

# Inicializa o banco ao importar este módulo
#iniciar_db()
