from typing import List

from flask import Flask, jsonify
from flask_cors import CORS

import api.common.rest
import api.database
from api import (
    admin,
    accounts,
    user_session,
    questions,
    quizzes,
    oauth,
    images,
    categories,
    status,
    errors
)


def init_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    root_endpoints: List[api.common.rest.ResourceEndpoints] = [
        admin.endpoints,
        user_session.endpoints,
        accounts.endpoints,
        questions.endpoints,
        quizzes.endpoints,
        oauth.endpoints,
        images.endpoints,
        categories.endpoints,
        status.endpoints,
    ]

    @app.errorhandler(404)
    def not_found(error):
        return jsonify([errors.api_error("resource_not_found")]), 404

    for resource_endpoints in root_endpoints:
        for resource_endpoint in resource_endpoints:
            app.add_url_rule(
                resource_endpoint[0],
                resource_endpoint[1],
                resource_endpoint[2],
                methods=[resource_endpoint[3]],
            )

    # Spawn database cleaner thread.
    cleaner = api.database.Cleaner()
    return app


if __name__ == "__main__":
    init_app().run(debug=True, port=5000)
