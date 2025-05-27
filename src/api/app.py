from flask import Flask

from src.api.routes import api_bp


def create_app():
    app = Flask(
        __name__, template_folder="../../templates", static_folder="../../static"
    )
    app.register_blueprint(api_bp)  # Register API routes Blueprint
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
