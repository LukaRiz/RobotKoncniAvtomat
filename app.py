# app.py - Main Flask application

from flask import Flask

from config import Config
from db import db
from core import RuleEngine

# Ustvari Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Inicializiraj bazo
db.init_app(app)

# Ustvari tabele
with app.app_context():
    db.create_all()

# Naloži pravila iz Excela
rules = RuleEngine()

# Registriraj blueprinte
from routes.main import main_bp, init_rules as init_main_rules
from routes.evaluate import evaluate_bp

# Nastavi rules engine v main blueprintu
init_main_rules(rules)

# Registriraj blueprinte
app.register_blueprint(main_bp)
app.register_blueprint(evaluate_bp)


if __name__ == "__main__":
    app.run(debug=True)
