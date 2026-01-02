import sqlite3
from logs import log_info, log_erro

def iniciar_db():
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ofertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco_atual TEXT,
            preco_antigo TEXT,
            link_original TEXT UNIQUE,
            link_afiliado TEXT,
            data_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            postada BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def salvar_oferta(nome, preco_atual, preco_antigo, link):
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO ofertas (nome, preco_atual, preco_antigo, link_original)
            VALUES (?, ?, ?, ?)
        ''', (nome, preco_atual, preco_antigo, link))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def buscar_ofertas_nao_convertidas(limite=5):
    """Retorna links originais que ainda precisam passar pelo conversor."""
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    # Pega apenas links que não foram convertidos E não foram postados
    cursor.execute("SELECT id, link_original FROM ofertas WHERE link_afiliado IS NULL AND postada = 0 LIMIT ?", (limite,))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

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

def buscar_proxima_oferta_para_postar():
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    # Garantimos que pegamos apenas onde postada é ZERO
    cursor.execute('''
        SELECT id, nome, preco_atual, preco_antigo, link_afiliado 
        FROM ofertas 
        WHERE link_afiliado IS NOT NULL AND postada = 0
        ORDER BY id ASC LIMIT 1
    ''')
    oferta = cursor.fetchone()
    conn.close()
    return oferta

# No database.py:
def marcar_como_postada(id_db):
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    # Atualiza ambos os campos para manter o banco organizado
    cursor.execute('''
        UPDATE ofertas 
        SET postada = 1
        WHERE id = ?
    ''', (id_db,))
    conn.commit()
    conn.close()

def limpar_banco_de_dados(dias=5):
    """Remove ofertas antigas (postas ou não) para manter o DB leve."""
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()
    try:
        # Note o uso de rowcount aqui
        cursor.execute(f"DELETE FROM ofertas WHERE data_captura < datetime('now', '-{dias} days')")
        removidos = cursor.rowcount
        conn.commit()
        if removidos > 0:
            log_info(f"🧹 Manutenção: {removidos} registros antigos removidos.")
        else:
            log_info("🧹 Manutenção: Nenhum registro antigo para remover.")
    except Exception as e:
        log_erro(f"⚠️ Falha na limpeza do banco: {e}")
    finally:
        conn.close()