from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Sistema de gestão de hotel rodando!"

if __name__ == "__main__":
    app.run(debug=True)
