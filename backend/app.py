from flask import Flask
from backend.routes import data_routes, risk_routes, governance_routes

app = Flask(__name__)
app.register_blueprint(data_routes.bp)
app.register_blueprint(risk_routes.bp)
app.register_blueprint(governance_routes.gov_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
