from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import date
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
    if len(document) != 11:
        flash("Document must contain exactly 11 digits.", "error")
        return redirect("/")


    try:
        conn = get_db_connection()
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

@app.route("/search_guest")
def search_guest():
    return render_template("search.html")

@app.route("/search_result", methods=["POST"])
def search_result():
    search_term = request.form['search_term']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT * FROM guests
        WHERE name LIKE %s OR document LIKE %s
    """
    search_like = f"%{search_term}%"
    cursor.execute(query, (search_like, search_like))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("search.html", results=results, search_term=search_term)

@app.route("/edit_guest/<int:guest_id>", methods=["GET"])
def edit_guest(guest_id):
    print(f"Tentando atualizar hóspede com ID {guest_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM guests WHERE id = %s", (guest_id,))
        guest = cursor.fetchone()
        cursor.close()
        conn.close()

        if guest:
            return render_template("edit_guest.html", guest=guest)
        else:
            flash("Guest not found.", "error")
            return redirect("/search_guest")
    except Exception as e:
        flash(f"An error occurred while loading guest data: {e}", "error")
        return redirect("/search_guest")

@app.route("/update_guest/<int:guest_id>", methods=["POST"])
def update_guest(guest_id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    document = request.form['document']
    if len(document) != 11:
        flash("Document must contain exactly 11 digits.", "error")
        return redirect(url_for("edit_guest", guest_id=guest_id))

    # Limpar dados
    import re
    name = re.sub(r'\s+', ' ', name.strip())
    phone = re.sub(r'\D', '', phone)
    document = re.sub(r'\D', '', document)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se já existe outro hóspede com o mesmo documento (exceto ele mesmo)
        cursor.execute("SELECT id FROM guests WHERE document = %s AND id != %s", (document, guest_id))
        existing = cursor.fetchone()
        if existing:
            flash("Document already exists for another guest.", "error")
            return redirect(url_for("edit_guest", guest_id=guest_id))

        # Atualizar dados
        cursor.execute("""
            UPDATE guests
            SET name = %s, email = %s, phone = %s, document = %s
            WHERE id = %s
        """, (name, email, phone, document, guest_id))

        conn.commit()
        cursor.close()
        conn.close()
        flash("Guest updated successfully!", "success")
        return redirect("/search_guest")

    except Exception as e:
        flash(f"An error occurred while updating: {e}", "error")
        return redirect(url_for("edit_guest", guest_id=guest_id))

@app.route("/delete_guest/<int:guest_id>", methods=["POST"])
def delete_guest(guest_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o hóspede existe
        cursor.execute("SELECT * FROM guests WHERE id = %s", (guest_id,))
        guest = cursor.fetchone()
        if not guest:
            flash("Guest not found.", "error")
            return redirect("/search_guest")

        # Deleta o hóspede
        cursor.execute("DELETE FROM guests WHERE id = %s", (guest_id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Guest deleted successfully.", "success")
        return redirect("/")
    except Exception as e:
        flash(f"An error occurred while deleting guest: {e}", "error")
        return redirect("/search_guest")

@app.route("/list_guests")
def list_guests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM guests ORDER BY name ASC")
        guests = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("search.html", results=guests, search_term="All Guests")

    except Exception as e:
        flash(f"An error occurred while listing guests: {e}", "error")
        return redirect("/")

@app.route("/reservation")
def reservation():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM guests")
        guests = cursor.fetchall()
        cursor.close()
        conn.close()
        today = date.today().isoformat()  # formato: YYYY-MM-DD
        return render_template("reservation.html", guests=guests, today=today)
    except Exception as e:
        flash(f"Error loading guests: {e}", "error")
        return redirect("/")


@app.route("/make_reservation", methods=["POST"])
def make_reservation():
    guest_id = request.form['guest_id']
    room_number = request.form['room_number'].strip()
    check_in_date = request.form['check_in_date']
    check_out_date = request.form['check_out_date']

    if not guest_id or not room_number or not check_in_date or not check_out_date:
        flash("All fields are required.", "error")
        return redirect("/reservation")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se o hóspede existe
        cursor.execute("SELECT id FROM guests WHERE id = %s", (guest_id,))
        guest = cursor.fetchone()

        if not guest:
            flash("Guest ID not found. Please verify and try again.", "error")
            return redirect("/")

        # Inserir reserva
        cursor.execute("""
            INSERT INTO reservations (guest_id, room_number, check_in_date, check_out_date)
            VALUES (%s, %s, %s, %s)
        """, (guest_id, room_number, check_in_date, check_out_date))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Reservation successfully created!", "success")
        return redirect("/reservation")

    except Exception as e:
        flash(f"An error occurred while making the reservation: {e}", "error")
        return redirect("/reservation")

@app.route('/list_reservations')
def list_reservations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query com JOIN para buscar o nome do hóspede
        query = """
                SELECT
                    r.id,
                    r.room_number,
                    r.check_in_date,
                    r.check_out_date,
                    g.name AS guest_name 
                FROM
                    reservations AS r
                JOIN
                    guests AS g ON r.guest_id = g.id
                ORDER BY
                    r.check_in_date ASC
            """
        cursor.execute(query)
        reservations_list = cursor.fetchall()

        # A rota /reservation também precisa da lista de hóspedes para o formulário
        cursor.execute("SELECT id, name FROM guests ORDER BY name ASC")
        guests_for_form = cursor.fetchall()

        cursor.close()
        conn.close()

        today = date.today().isoformat()

        # Passamos as duas listas para o template
        return render_template(
            'reservation.html',
            reservations=reservations_list,
            guests=guests_for_form,
        )

    except Exception as e:
        flash(f"An error occurred while listing reservations: {e}", "error")
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
