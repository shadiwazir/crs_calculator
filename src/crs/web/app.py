"""Flask application: serves the calculator page and a JSON scoring endpoint."""
from flask import Flask, jsonify, render_template, request

from ..calculator import calculate
from ..models import ValidationError
from .schema import parse_profile, test_options


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html", tests=test_options())

    @app.post("/api/calculate")
    def api_calculate():
        try:
            profile = parse_profile(request.get_json(silent=True))
        except ValidationError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(calculate(profile).to_dict())

    return app
