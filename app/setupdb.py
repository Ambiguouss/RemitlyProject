from models import db
from parse import parse_swift_data
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
    parse_swift_data("Interns_2025_SWIFT_CODES - Sheet1.csv")
