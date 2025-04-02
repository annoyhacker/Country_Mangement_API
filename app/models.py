from datetime import datetime
from .database import db

neighbours = db.Table('country_neighbours',
    db.Column('country_id', db.Integer, db.ForeignKey('countries.id'), primary_key=True),
    db.Column('neighbour_id', db.Integer, db.ForeignKey('countries.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

class Country(db.Model):
    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cca3 = db.Column(db.String(3), nullable=False)
    currency_code = db.Column(db.String(10))
    currency = db.Column(db.String(50))
    capital = db.Column(db.String(100))
    region = db.Column(db.String(50))
    subregion = db.Column(db.String(50))
    area = db.Column(db.BigInteger)
    map_url = db.Column(db.String(255))
    population = db.Column(db.BigInteger)
    flag_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    neighboring_countries = db.relationship(
        'Country',
        secondary=neighbours,
        primaryjoin=(neighbours.c.country_id == id),
        secondaryjoin=(neighbours.c.neighbour_id == id),
        backref='neighboured_by'
    )