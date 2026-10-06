from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request
from flask_login import login_required

from models.model import Match, Competition


app = Blueprint("frontend", __name__)


TIMEZONE = ZoneInfo("Europe/Zurich")

FINISHED_STATUSES = ["FT", "AET", "PEN"]


@app.route("/")
@login_required
def home():

    # Data di oggi nel fuso orario dell'applicazione
    today = datetime.now(TIMEZONE).date()

    # Competizione selezionata dalla barra di ricerca
    selected_competition = request.args.get("competition")

    # Recupera tutte le competizioni presenti nel database
    competitions = Competition.query.order_by(
        Competition.name
    ).all()

    # Recupera tutte le partite concluse di oggi
    query = Match.query.filter(
        Match.date >= datetime.combine(today, datetime.min.time()),
        Match.date < datetime.combine(
            today,
            datetime.max.time()
        ),
        Match.status.in_(FINISHED_STATUSES)
    )

    # Se è stata selezionata una competizione,
    # mostra solamente le sue partite
    if selected_competition:
        query = query.join(Competition).filter(
            Competition.name == selected_competition
        )

    matches = query.order_by(Match.date).all()

    # Raggruppa le partite per competizione
    matches_by_competition = {}

    for match in matches:

        competition = match.competition

        if competition.id not in matches_by_competition:
            matches_by_competition[competition.id] = {
                "competition": competition,
                "matches": []
            }

        matches_by_competition[competition.id]["matches"].append(match)

    competition_groups = list(matches_by_competition.values())

    # Competizioni configurate come "maggiori"
    major_competitions = [
        group
        for group in competition_groups
        if group["competition"].is_major
    ]

    # Durante lo sviluppo, se nessuna competizione è ancora
    # configurata come maggiore, mostriamo comunque i dati.
    if not major_competitions:
        major_competitions = competition_groups

    # Competizione principale configurata per il paese.
    # La personalizzazione per singolo utente verrà aggiunta
    # quando il modello User conterrà il paese.
    regional_competition = next(
        (
            group
            for group in competition_groups
            if group["competition"].is_top_in_country
        ),
        None
    )

    return render_template(
        "home.html",
        competitions=competitions,
        regional_competition=regional_competition,
        major_competitions=major_competitions,
        selected_competition=selected_competition
    )