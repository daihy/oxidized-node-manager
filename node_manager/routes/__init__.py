"""
Routes package - Flask route blueprints.
"""

from flask import Blueprint

# Create blueprints
nodes_bp = Blueprint("nodes", __name__)
auth_bp = Blueprint("auth", __name__)
oxidized_api_bp = Blueprint("oxidized_api", __name__)
config_bp = Blueprint("config", __name__)

# Import routes to register them with blueprints
from routes import nodes, auth, oxidized_api, config_api, models_api
from routes.groups_api import groups_bp
from routes.models_api import models_bp
from routes.credentials_api import credentials_bp
from routes.pages import pages_bp
