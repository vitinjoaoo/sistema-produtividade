import sqlite3
import hashlib

def criar_admin_mestre():
    """
    Script utilitário para inserir manualmente o Administrador principal no banco de dados.
    Essencial para o primeiro acesso ao sistema após a criação das tabelas.
    """
    # Estabelece conexão com o arquivo de banco de dados local
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()

    # --- CONFIGURAÇÃO DAS CREDENCIAIS MESTRE ---
    usuario = "admin"
    senha_plana = "1234"  # Senha em texto puro (será criptografada abaixo)
    nome = "Administrador Geral"
    perfil = "Administrador Presencial"
    email = "joaomoulindantas@hotmail.com"

    # --- PROTOCOLO DE SEGURANÇA: HASHING ---
    # Transforma a senha "1234" em uma sequência hexadecimal de 64 caracteres.
    # O SHA-256 é um algoritmo de via única; o banco nunca conhecerá a senha real, apenas o hash.
    senha_hash = hashlib.sha256(senha_plana.encode()).hexdigest()

    try:
        # Execução do comando SQL INSERT para persistência dos dados
        # Os '?' são placeholders que evitam ataques de SQL Injection
        c.execute("INSERT INTO usuarios (username, password, nome, perfil, email) VALUES (?, ?, ?, ?, ?)",
                  (usuario, senha_hash, nome, perfil, email))
        
        # Confirma a transação no disco rígido
        conn.commit()
        print(f"✅ Administrador '{usuario}' criado com sucesso!")
        print(f"🔑 Senha temporária: {senha_plana}")
        print("💡 Lembre-se de alterar esta senha após o primeiro login por segurança.")
        
    except sqlite3.IntegrityError:
        # Tratamento de erro caso a PRIMARY KEY (username) já esteja ocupada
        print("⚠️ Erro: Este usuário já existe. Não é possível duplicar o acesso mestre.")
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        
    finally:
        # Garante o fechamento da conexão com o banco de dados independente do resultado
        conn.close()

if __name__ == "__main__":
    criar_admin_mestre()