from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SwiftCode(db.Model):
    __tablename__ = 'swift_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    bank_name = db.Column(db.String(255), nullable=False)
    country_iso2 = db.Column(db.String(2), nullable=False)
    country_name = db.Column(db.String(255), nullable=False)
    is_headquarter = db.Column(db.Boolean, default=False)
    swift_code = db.Column(db.String(11), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<SwiftCode {self.swift_code}>'
