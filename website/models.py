from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    code = db.Column(db.String(10))
    loans_as_owner = db.relationship('Loan', back_populates='owner', foreign_keys='Loan.owner_id')
    loans_as_borrower = db.relationship('Loan', back_populates='borrower', foreign_keys='Loan.borrower_id')
    
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    purpose = db.Column(db.String(200))
    accepted = db.Column(db.Boolean)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    owner = db.relationship('User', back_populates='loans_as_owner', foreign_keys=[owner_id])
    borrower = db.relationship('User', back_populates='loans_as_borrower', foreign_keys=[borrower_id])