from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    availability_status = db.Column(db.Boolean, default=True)

