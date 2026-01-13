from flask import Flask, jsonify
from flask_cors import CORS
from backend.routes import data_routes, risk_routes, governance_routes
from backend.config import Config
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Configure Logging
    logging.basicConfig(level=app.config['LOG_LEVEL'])
    logger = logging.getLogger(__name__)

    # Register Blueprints
    app.register_blueprint(data_routes.bp)
    app.register_blueprint(risk_routes.bp)
    app.register_blueprint(governance_routes.gov_bp)

    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=app.config['PORT'], debug=app.config['DEBUG'])
