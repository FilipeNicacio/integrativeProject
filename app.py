from flask import Flask
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'integrativeproject_db'
}

@app.route("/")
def home():
    return "Sistema de gestão de hotel rodando!"

def get_db_connection():
    return mysql.connector.connect(**db_config)

if __name__ == "__main__":

    print("Iniciando o servidor Flask e testando conexão com o banco de dados...")

    try:
        conn = get_db_connection()
        print("Conexão com banco de dados estabelecida com sucesso!")
        conn.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")

    app.run(debug=True)
