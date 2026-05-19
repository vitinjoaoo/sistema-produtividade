import sqlite3
import hashlib

def criar_tabela_usuarios():
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (username TEXT PRIMARY KEY, password TEXT, nome TEXT)''')
    conn.commit()
    conn.close()

def cadastrar_usuario(username, password, nome):
    try:
        conn = sqlite3.connect('produtividade.db')
        c = conn.cursor()
        # Hash da senha para segurança (não salvamos senha limpa)
        senha_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO usuarios VALUES (?, ?, ?)", (username, senha_hash, nome))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def verificar_login(username, password):
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    senha_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, senha_hash))
    user = c.fetchone()
    conn.close()
    return user