import sqlite3
import os
from logs import log_info, log_erro


def get_db_name(usuario):
    """Gera o nome do arquivo de banco de dados baseado no usuário."""
    nome_limpo = usuario.strip().lower().replace(" ", "_")
    return f"ofertas_{nome_limpo}.db"


def iniciar_db(usuario="padrao"):
    db_name = get_db_name(usuario)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS ofertas
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       nome
                       TEXT,
                       preco_atual
                       TEXT,
                       preco_antigo
                       TEXT,
                       link_original
                       TEXT
                       UNIQUE,
                       link_afiliado
                       TEXT,
                       data_captura
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       postada
                       BOOLEAN
                       DEFAULT
                       FALSE,
                       termo_busca
                       TEXT
                       DEFAULT
                       ''
                   )
                   ''')

    # Garantia de compatibilidade se o banco já existir
    try:
        cursor.execute("ALTER TABLE ofertas ADD COLUMN termo_busca TEXT DEFAULT ''")
    except:
        pass

    conn.commit()
    conn.close()


def salvar_oferta(nome, preco_atual, preco_antigo, link, termo="", usuario="padrao"):
    db_name = get_db_name(usuario)
    termo_limpo = termo.strip().lower() if termo else "flash_sale"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute('''
                       INSERT INTO ofertas (nome, preco_atual, preco_antigo, link_original, termo_busca)
                       VALUES (?, ?, ?, ?, ?)
                       ''', (nome, preco_atual, preco_antigo, link, termo_limpo))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def buscar_ofertas_por_termo_para_converter(termo="", limite=5, usuario="padrao"):
    db_name = get_db_name(usuario)
    termo_limpo = termo.strip().lower() if termo else "flash_sale"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT id, link_original
                   FROM ofertas
                   WHERE link_afiliado IS NULL
                     AND postada = 0
                     AND termo_busca = ? LIMIT ?
                   ''', (termo_limpo, limite))
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def atualizar_link_afiliado(id_oferta, link_convertido, usuario="padrao"):
    db_name = get_db_name(usuario)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('UPDATE ofertas SET link_afiliado = ? WHERE id = ?', (link_convertido, id_oferta))
    conn.commit()
    conn.close()


def buscar_proxima_oferta_para_postar(termo="", usuario="padrao"):
    db_name = get_db_name(usuario)
    termo_limpo = termo.strip().lower() if termo else "flash_sale"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT id, nome, preco_atual, preco_antigo, link_afiliado
                   FROM ofertas
                   WHERE link_afiliado IS NOT NULL
                     AND postada = 0
                     AND termo_busca = ?
                   ORDER BY id ASC LIMIT 1
                   ''', (termo_limpo,))
    oferta = cursor.fetchone()
    conn.close()
    return oferta


def marcar_como_postada(id_db, usuario="padrao"):
    db_name = get_db_name(usuario)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('UPDATE ofertas SET postada = 1 WHERE id = ?', (id_db,))
    conn.commit()
    conn.close()


def contar_ofertas_pendentes(termo="", usuario="padrao"):
    db_name = get_db_name(usuario)
    termo_limpo = termo.strip().lower() if termo else "flash_sale"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ofertas WHERE postada = 0 AND termo_busca = ?", (termo_limpo,))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def limpar_banco_de_dados(dias=5, usuario="padrao"):
    db_name = get_db_name(usuario)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM ofertas WHERE data_captura < datetime('now', '-{dias} days')")
        removidos = cursor.rowcount
        conn.commit()
        log_info(f"🧹 Manutenção ({usuario}): {removidos} registros removidos.")
    except Exception as e:
        log_erro(f"⚠️ Falha na limpeza do banco ({usuario}): {e}")
    finally:
        conn.close()

def buscar_oferta_aleatoria_pronta(usuario="padrao"):
    import sqlite3
    db_name = f"ofertas_{usuario.strip().lower().replace(' ', '_')}.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Pega qualquer item que tenha link_afiliado, não foi postado, em ordem aleatória
    cursor.execute('''
        SELECT id, nome, preco_atual, preco_antigo, link_afiliado
        FROM ofertas
        WHERE link_afiliado IS NOT NULL
          AND postada = 0
        ORDER BY RANDOM() LIMIT 1
    ''')
    oferta = cursor.fetchone()
    conn.close()
    return oferta