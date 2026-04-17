"""
Routes package - Flask route blueprints.
"""

from flask import Blueprint

# Create blueprints
nodes_bp = Blueprint("nodes", __name__)
auth_bp = Blueprint("auth", __name__)
oxidized_api_bp = Blueprint("oxidized_api", __name__)

# Import routes to register them with blueprints
from routes import nodes, auth, oxidized_api
