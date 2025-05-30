from flask import Flask, render_template, request, redirect
import mysql.connector
import re

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'integrativeproject_db'
}

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/guest_registration", methods=["POST"])
def guest_registration():
    name = request.form['name'].strip()
    email = request.form['email'].strip()
    phone = request.form['phone'].strip()
    document = request.form['document'].strip()

    name = re.sub(r'\s+', ' ', name)  # Remove espaços duplos, triplos etc.
    phone = re.sub(r'\D', '', phone)  # Remove tudo que não for número
    document = re.sub(r'\D', '', document)  # Remove pontuações do documento

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO guests (name, email, phone, document) VALUES (%s, %s, %s, %s)",
                       (name, email, phone, document))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/")
    except Exception as e:
        return f"Erro ao cadastrar hóspede: {e}"

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
