from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, session
from datetime import date
import mysql.connector
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'hotel'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'integrativeproject_db'
}

def create_admin_user():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if cursor.fetchone() is None:
            hashed_password = generate_password_hash('admin')
            cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
                           ('admin', hashed_password, 1))
            conn.commit()
            print(">>> User 'admin' created successfully. Password: 'admin")
        else:
            print(">>> User 'admin' already exists.")

    except Exception as e:
        print(f"Error creating user 'admin': {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def home():
    return render_template('index.html')

@app.route("/guest_registration", methods=["POST"])
@login_required
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
@login_required
def search_guest():
    return render_template("search.html")

@app.route("/search_result", methods=["POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
        return redirect("/search_guest")

    except Exception as e:
        flash(f"An error occurred while deleting guest: {e}", "error")
        return redirect("/search_guest")

@app.route("/list_guests")
@login_required
def list_guests():

    search_term = request.args.get('search', '').strip()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if search_term:
            query = "SELECT * FROM guests WHERE name LIKE %s OR document LIKE %s ORDER BY name ASC"
            search_like = f"%{search_term}%"
            cursor.execute(query, (search_like, search_like))
        else:
            # Se não, lista todos os hóspedes
            query = "SELECT * FROM guests ORDER BY name ASC"
            cursor.execute(query)

        guests = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("search.html", results=guests, search_term="All Guests")

    except Exception as e:
        flash(f"An error occurred while listing guests: {e}", "error")
        return redirect("/")

@app.route("/reservation")
@login_required
def reservation():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM guests")
        guests = cursor.fetchall()
        cursor.execute("SELECT id, number FROM floors ORDER BY number ASC")
        floors = cursor.fetchall()
        cursor.close()
        conn.close()
        today = date.today().isoformat()  # formato: YYYY-MM-DD
        return render_template("reservation.html", guests=guests, floors=floors, today=today)
    except Exception as e:
        flash(f"Error loading guests: {e}", "error")
        return redirect("/")

@app.route("/get_rooms_by_floor/<int:floor_id>")
@login_required
def get_rooms_by_floor(floor_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, room_number FROM rooms WHERE floor_id = %s ORDER BY room_number ASC", (floor_id,))
        rooms = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rooms)
    except Exception as e:
        return jsonify({"Fatal error": str(e)}), 500



@app.route("/make_reservation", methods=["POST"])
@login_required
def make_reservation():
    guest_id = request.form['guest_id']
    room_id = request.form.get('room_id')
    check_in_date = request.form['check_in_date']
    check_out_date = request.form['check_out_date']

    if not guest_id or not room_id or not check_in_date or not check_out_date:
        flash("All fields are required.", "error")
        return redirect("/reservation")

    if check_out_date < check_in_date:
        flash("Check-out date cannot be earlier than check-in date.", "error")
        return redirect(url_for('reservation'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # A consulta verifica se existe alguma reserva para o mesmo quarto
        query_check_conflict = """
                    SELECT id FROM reservations
                    WHERE room_id = %s
                    AND check_in_date < %s
                    AND check_out_date > %s
                """
        cursor.execute(query_check_conflict, (room_id, check_out_date, check_in_date))
        conflicting_reservation = cursor.fetchone()

        if conflicting_reservation:
            flash("This room is already booked for the selected dates. Please choose different dates or another room.",
                  "error")
            cursor.close()
            conn.close()
            return redirect(url_for('reservation'))

        # Verificar se o hóspede existe
        cursor.execute("SELECT id FROM guests WHERE id = %s", (guest_id,))
        guest = cursor.fetchone()

        if not guest:
            flash("Guest ID not found. Please verify and try again.", "error")
            return redirect("/")

        # Verificar se o quarto existe
        cursor.execute("SELECT id FROM rooms WHERE id = %s", (room_id,))
        if not cursor.fetchone():
            flash("Room not found.", "error")
            return redirect(url_for('reservation'))

        # Inserir reserva
        cursor.execute("""
            INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date)
            VALUES (%s, %s, %s, %s)
        """, (guest_id, room_id, check_in_date, check_out_date))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Reservation successfully created!", "success")
        return redirect("/reservation")

    except Exception as e:
        flash(f"An error occurred while making the reservation: {e}", "error")
        return redirect("/reservation")

@app.route('/list_reservations')
@login_required
def list_reservations():

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    reservations_list = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT r.id, r.check_in_date, r.check_out_date, g.id AS guest_id, 
                   g.name AS guest_name, ro.room_number, f.number AS floor_number 
            FROM reservations AS r
            JOIN guests AS g ON r.guest_id = g.id
            JOIN rooms AS ro ON r.room_id = ro.id
            JOIN floors AS f ON ro.floor_id = f.id
        """

        conditions = []
        params = []

        if start_date:
            conditions.append("r.check_in_date >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("r.check_in_date <= %s")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY r.check_in_date ASC"

        cursor.execute(query, tuple(params))
        reservations_list = cursor.fetchall()
        cursor.close()
        conn.close()

    except Exception as e:
        flash(f"An error occurred while listing reservations: {e}", "error")
        return redirect("/")

    return render_template('list_reservations.html',
                           reservations=reservations_list,
                           filters={'start_date': start_date, 'end_date': end_date})


@app.route("/get_booked_dates/<int:room_id>")
@login_required
def get_booked_dates(room_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Seleciona as datas de check-in e check-out para o quarto específico
        query = "SELECT check_in_date, check_out_date FROM reservations WHERE room_id = %s"
        cursor.execute(query, (room_id,))

        booked_dates = cursor.fetchall()
        cursor.close()
        conn.close()

        date_ranges = []

        for booking in booked_dates:
            date_ranges.append({
                "from": booking['check_in_date'].isoformat(),
                "to": booking['check_out_date'].isoformat()
            })

        return jsonify(date_ranges)

    except Exception as e:
        flash(f"An error occurred while selecting the check-in and check-out date: {e}", "error")
        return redirect("/")

@app.route('/guest_details/<int:guest_id>')
@login_required
def guest_details(guest_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM guests WHERE id = %s", (guest_id,))
        guest = cursor.fetchone()
        cursor.close()
        conn.close()

        if guest:
            return render_template('guest_details.html', guest=guest)
        else:
            flash("Guest not found.", "error")
            return redirect(url_for('list_reservations'))

    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('list_reservations'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

def get_db_connection():
    return mysql.connector.connect(**db_config)

if __name__ == "__main__":

    print("Iniciando o servidor Flask e testando conexão com o banco de dados...")
    create_admin_user()

    try:
        conn = get_db_connection()
        print("Conexão com banco de dados estabelecida com sucesso!")
        conn.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")

    app.run(debug=True)
