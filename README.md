# 🏨 Hotel Management System

A web-based Hotel Management System developed with **Python, Flask, and MySQL** to streamline guest registration and reservation management.

This project was created as part of the **Integrative Project** course and demonstrates the application of full-stack web development concepts, database integration, and CRUD operations in a real-world hospitality scenario.

---

## 📋 Overview

The Hotel Management System provides a centralized platform for managing hotel guests and reservations. The application allows hotel staff to efficiently register guests, search and update records, and manage reservations through an intuitive web interface.

The system follows a traditional client-server architecture and uses a MySQL database for persistent data storage.

---

## ✨ Features

### Guest Management

* Register new guests
* Search guests by information
* View guest details
* Update guest records
* Delete guest records

### Reservation Management

* Create reservations
* View reservation list
* Manage reservation information

### Authentication

* User login system
* Protected routes using authentication

### User Interface

* Responsive web pages
* Simple and intuitive navigation
* Organized data presentation

---

## 🛠️ Technology Stack

| Category                | Technology    |
| ----------------------- | ------------- |
| Backend                 | Python        |
| Framework               | Flask         |
| Database                | MySQL         |
| Frontend                | HTML5, CSS3   |
| Authentication          | Flask Session |
| Development Environment | PyCharm       |

---

## 📁 Project Structure

```text
integrativeProject/
│
├── app.py
├── integrativeproject_db.sql
├── requirements.txt
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── search.html
│   ├── edit_guest.html
│   ├── guest_details.html
│   ├── reservation.html
│   └── list_reservations.html
│
└── static/
    └── css/
        └── style.css
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/FilipeNicacio/integrativeProject.git
cd integrativeProject
```

### 2. Create the Database

Create a MySQL database named:

```sql
CREATE DATABASE integrativeproject_db;
```

### 3. Import the SQL Script

Import the file:

```text
integrativeproject_db.sql
```

into the database created in the previous step.

### 4. Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

If the requirements file is unavailable, install manually:

```bash
pip install flask
pip install mysql-connector-python
pip install werkzeug
```

### 5. Configure Database Connection

Verify the database configuration inside `app.py`:

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'integrativeproject_db'
}
```

Adjust the credentials according to your local MySQL configuration.

### 6. Run the Application

```bash
python app.py
```

The application will be available at:

```text
http://localhost:5000
```

---

## 🧪 Evaluation Instructions

To successfully execute the project:

1. Ensure MySQL Server is running.
2. Create the database `integrativeproject_db`.
3. Import the provided SQL file.
4. Install the required Python dependencies.
5. Run the application using:

```bash
python app.py
```

---
