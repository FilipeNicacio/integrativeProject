from flask import Flask, render_template, request, redirect, flash
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = 'hotel'

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
    phone = re.sub(r'\D', '', request.form['phone'])
    document = re.sub(r'\D', '', request.form['document'].strip())


    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verificar duplicidade de documento
        cursor.execute("SELECT * FROM guests WHERE document = %s", (document,))
        existing_guest = cursor.fetchone()

        if existing_guest:
            flash("A guest with this document is already registered. Please check the information and try again.", "error")
        else:
            # Inserção no banco
            cursor.execute("INSERT INTO guests (name, email, phone, document) VALUES (%s, %s, %s, %s)",
                           (name, email, phone, document))
            conn.commit()
            flash("Guest successfully registered!", "success")

        cursor.close()
        conn.close()
        return redirect("/")

    except Exception as e:
        flash(f"An error occurred during registration: {e}", "error")
        return redirect("/")

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
