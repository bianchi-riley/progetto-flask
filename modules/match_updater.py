from datetime import datetime
from zoneinfo import ZoneInfo

from models.conn import db
from models.model import Competition, Team, Match

from modules.football_api import get_finished_matches


TIMEZONE = ZoneInfo("Europe/Zurich")


def update_matches(match_date=None):
    """
    Recupera le partite concluse da API-Football
    e aggiorna il database.

    Le competizioni, le squadre e le partite vengono
    ricercate tramite il loro api_id per evitare duplicati.
    """

    matches_data = get_finished_matches(match_date)

    created_matches = 0
    updated_matches = 0

    for match_data in matches_data:

        fixture = match_data["fixture"]
        league = match_data["league"]
        teams = match_data["teams"]
        goals = match_data["goals"]

        # ---------------------------------------------------------
        # COMPETITION
        # ---------------------------------------------------------

        competition = Competition.query.filter_by(
            api_id=league["id"]
        ).first()

        if competition is None:
            competition = Competition(
                api_id=league["id"],
                name=league["name"],
                country=league.get("country", "Unknown"),
                country_code=None,
                logo=league.get("logo"),
                type=None
            )

            db.session.add(competition)
            db.session.flush()


        # ---------------------------------------------------------
        # HOME TEAM
        # ---------------------------------------------------------

        home_team = Team.query.filter_by(
            api_id=teams["home"]["id"]
        ).first()

        if home_team is None:
            home_team = Team(
                api_id=teams["home"]["id"],
                name=teams["home"]["name"],
                logo=teams["home"].get("logo"),
                country=None
            )

            db.session.add(home_team)
            db.session.flush()


        # ---------------------------------------------------------
        # AWAY TEAM
        # ---------------------------------------------------------

        away_team = Team.query.filter_by(
            api_id=teams["away"]["id"]
        ).first()

        if away_team is None:
            away_team = Team(
                api_id=teams["away"]["id"],
                name=teams["away"]["name"],
                logo=teams["away"].get("logo"),
                country=None
            )

            db.session.add(away_team)
            db.session.flush()


        # ---------------------------------------------------------
        # MATCH
        # ---------------------------------------------------------

        match = Match.query.filter_by(
            api_id=fixture["id"]
        ).first()

        # API-Football restituisce la data ISO con "Z"
        match_datetime = datetime.fromisoformat(
            fixture["date"].replace("Z", "+00:00")
        )

        # Convertiamo la data nel fuso dell'applicazione
        match_datetime = match_datetime.astimezone(TIMEZONE)

        # Il nostro modello usa DateTime senza timezone
        match_datetime = match_datetime.replace(tzinfo=None)


        if match is None:

            match = Match(
                api_id=fixture["id"],
                competition=competition,
                home_team=home_team,
                away_team=away_team,
                date=match_datetime,
                status=fixture["status"]["short"],
                home_score=goals.get("home"),
                away_score=goals.get("away")
            )

            db.session.add(match)

            created_matches += 1

        else:

            # Aggiorniamo i dati nel caso il risultato
            # sia cambiato rispetto alla precedente chiamata.
            match.competition = competition
            match.home_team = home_team
            match.away_team = away_team
            match.date = match_datetime
            match.status = fixture["status"]["short"]
            match.home_score = goals.get("home")
            match.away_score = goals.get("away")

            updated_matches += 1


    db.session.commit()

    return 