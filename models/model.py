from flask_login import UserMixin
from models.conn import db
from werkzeug.security import generate_password_hash, check_password_hash

user_competitions = db.Table(
    "user_competitions",

    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True
    ),

    db.Column(
        "competition_id",
        db.Integer,
        db.ForeignKey("competition.id"),
        primary_key=True
    )
)

# The UserMixin will add Flask-Login attributes to the model so that Flask-Login will be able to work with it.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Campo per la password criptata

    competitions = db.relationship(
    "Competition",
    secondary=user_competitions,
    back_populates="users"
)

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User username:{self.username}, email:{self.email}>'
    
class Competition(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # ID della competizione su API-Football
    api_id = db.Column(db.Integer, unique=True, nullable=False)

    name = db.Column(db.String(100), nullable=False)

    country = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(2), nullable=True)

    logo = db.Column(db.String(255), nullable=True)

    # league / cup
    type = db.Column(db.String(20), nullable=True)

    # Indica se deve comparire nella sezione "Maggiori competizioni"
    is_major = db.Column(db.Boolean, default=False, nullable=False)

    # Indica se è il principale campionato del paese
    is_top_in_country = db.Column(db.Boolean, default=False, nullable=False)

    users = db.relationship(
    "User",
    secondary=user_competitions,
    back_populates="competitions"
)

    matches = db.relationship(
        "Match",
        back_populates="competition",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Competition {self.name}>"
    
class Team(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # ID della squadra su API-Football
    api_id = db.Column(db.Integer, unique=True, nullable=False)

    name = db.Column(db.String(100), nullable=False)

    logo = db.Column(db.String(255), nullable=True)

    country = db.Column(db.String(100), nullable=True)

    home_matches = db.relationship(
        "Match",
        foreign_keys="Match.home_team_id",
        back_populates="home_team"
    )

    away_matches = db.relationship(
        "Match",
        foreign_keys="Match.away_team_id",
        back_populates="away_team"
    )

    def __repr__(self):
        return f"<Team {self.name}>"
    
class Match(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # ID della partita su API-Football
    api_id = db.Column(db.Integer, unique=True, nullable=False)

    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("competition.id"),
        nullable=False
    )

    home_team_id = db.Column(
        db.Integer,
        db.ForeignKey("team.id"),
        nullable=False
    )

    away_team_id = db.Column(
        db.Integer,
        db.ForeignKey("team.id"),
        nullable=False
    )

    # Data e ora della partita
    date = db.Column(db.DateTime, nullable=False)

    # FT, AET, PEN, ecc.
    status = db.Column(db.String(20), nullable=False)

    # Risultato finale
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)

    competition = db.relationship(
        "Competition",
        back_populates="matches"
    )

    home_team = db.relationship(
        "Team",
        foreign_keys=[home_team_id],
        back_populates="home_matches"
    )

    away_team = db.relationship(
        "Team",
        foreign_keys=[away_team_id],
        back_populates="away_matches"
    )

    def __repr__(self):
        return f"<Match {self.home_team_id} vs {self.away_team_id}>"