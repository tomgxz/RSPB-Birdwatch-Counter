from flask_login import UserMixin
from __init__ import db

class User(UserMixin,db.Model):
    __tablename__="user"
    user_id = db.Column( db.String, primary_key=True)
        # PK user_id TEXT
    password = db.Column( db.String, nullable=False)
        # password TEXT NOT NULL
    robin = db.Column( db.Integer )
        # robin INT
    blackbird = db.Column( db.Integer )
        # blackbird INT
    pigeon = db.Column( db.Integer )
        # pigeon INT
    magpie = db.Column( db.Integer )
        # magpie INT
    blue_tit = db.Column( db.Integer )
        # blue_tit INT
    thrush = db.Column( db.Integer )
        # thrush INT
    wren = db.Column( db.Integer )
        # wren INT
    starling = db.Column( db.Integer )
        # starling INT

    def get_id(self): return self.user_id

    def robinCount(self): return self.robin
    def blackbirdCount(self): return self.blackbird
    def pigeonCount(self): return self.pigeon
    def magpieCount(self): return self.magpie
    def bluetitCount(self): return self.blue_tit
    def thrushCount(self): return self.thrush
    def wrenCount(self): return self.wren
    def starlingCount(self): return self.starling
