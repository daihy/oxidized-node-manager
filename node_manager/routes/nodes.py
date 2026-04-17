"""
Nodes routes - CRUD operations for network devices.
"""

from flask import request, jsonify
from routes import nodes_bp
from routes.auth import login_required
from models.node import Node
import requests
import os

# Configuration (will be set by app.py)
OXIDIZED_API_URL = os.getenv("OXIDIZED_API_URL", "http://oxidized:8888")
CONFIG_FILE = os.getenv("CONFIG_FILE", "/oxidized_config/nodes.csv")


def set_config(oxidized_url, config_file):
    """Set configuration from app.py."""
    global OXIDIZED_API_URL, CONFIG_FILE
    OXIDIZED_API_URL = oxidized_url
    CONFIG_FILE = config_file


def reload_oxidized_nodes():
    """Trigger Oxidized to reload node list."""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/reload.json", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Warning: Failed to reload Oxidized nodes: {e}")
        return False


def delete_oxidized_node(node_name):
    """Delete a node from Oxidized."""
    try:
        response = requests.delete(
            f"{OXIDIZED_API_URL}/node/{node_name}.json", timeout=10
        )
        if response.status_code == 200:
            return {"success": True}
        return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"Error deleting Oxidized node {node_name}: {e}")
        return {"success": False, "error": str(e)}


def write_nodes_csv(nodes):
    """Write nodes to CSV for Oxidized."""
    import csv

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "ip", "model", "protocol", "port", "username", "password"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for node in nodes:
            model_id = node.get("model", "")
            model_name = model_id.lower() if model_id else ""
            writer.writerow(
                {
                    "name": node.get("name", ""),
                    "ip": node.get("ip", ""),
                    "model": model_name,
                    "protocol": node.get("protocol", ""),
                    "port": node.get("port", ""),
                    "username": node.get("username", ""),
                    "password": node.get("password", ""),
                }
            )


@nodes_bp.route("/api/nodes", methods=["GET", "POST"])
@login_required
def get_nodes():
    """Get all nodes or add a new node."""
    if request.method == "GET":
        nodes = Node.get_all()
        return jsonify([n.to_dict() for n in nodes])

    if request.method == "POST":
        data = request.json
        name = data.get("name")

        # Check if node already exists
        existing = Node.get_by_name(name)
        if existing:
            return jsonify({"success": False, "error": "Node already exists"})

        # Validate port
        try:
            port = int(data.get("port", 22))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Port must be a valid number"})

        # Create new node in database
        model_id = data.get("model", "")
        node = Node(
            name=name,
            ip=data.get("ip", ""),
            model=model_id.lower() if model_id else "",
            protocol=data.get("protocol", "ssh"),
            port=port,
            username=data.get("username", ""),
            password=data.get("password", ""),
        )
        node.save()

        # Sync to CSV for Oxidized
        all_nodes = Node.get_all()
        write_nodes_csv([n.to_dict() for n in all_nodes])
        reload_oxidized_nodes()

        return jsonify({"success": True})


@nodes_bp.route("/api/nodes/<name>", methods=["GET", "PUT", "DELETE"])
@login_required
def node_detail(name):
    """Get, update, or delete a specific node."""
    node = Node.get_by_name(name)

    if request.method == "GET":
        if node:
            return jsonify(node.to_dict())
        return jsonify({"error": "Node not found"}), 404

    if request.method == "PUT":
        if not node:
            return jsonify({"success": False, "error": "Node not found"}), 404

        data = request.json
        node.ip = data.get("ip", node.ip)
        node.model = (
            data.get("model", node.model).lower() if data.get("model") else node.model
        )
        node.protocol = data.get("protocol", node.protocol)
        try:
            node.port = int(data.get("port", node.port))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Port must be a valid number"})
        node.username = data.get("username", node.username)
        node.password = data.get("password", node.password)
        node.save()

        # Sync to CSV for Oxidized
        all_nodes = Node.get_all()
        write_nodes_csv([n.to_dict() for n in all_nodes])
        reload_oxidized_nodes()

        return jsonify({"success": True})

    if request.method == "DELETE":
        # Delete from Oxidized first
        delete_oxidized_node(name)

        # Delete from database
        if node:
            node.delete()

        # Sync to CSV for Oxidized
        all_nodes = Node.get_all()
        write_nodes_csv([n.to_dict() for n in all_nodes])
        reload_oxidized_nodes()

        return jsonify({"success": True})


@nodes_bp.route("/api/import", methods=["POST"])
def import_nodes():
    """Import nodes from CSV content."""
    data = request.json
    csv_content = data.get("csv", "")

    try:
        lines = csv_content.strip().split("\n")
        new_nodes = []
        for line in lines:
            if line.strip() and not line.startswith("#"):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    new_nodes.append(
                        {
                            "name": parts[0],
                            "ip": parts[1],
                            "model": parts[2],
                            "protocol": parts[3] if len(parts) > 3 else "ssh",
                            "port": parts[4]
                            if len(parts) > 4
                            else (
                                "32410"
                                if len(parts) > 3 and parts[3] == "ssh"
                                else "23"
                            ),
                            "username": parts[5] if len(parts) > 5 else "",
                            "password": parts[6] if len(parts) > 6 else "",
                        }
                    )

        # Import each node to database
        for node_data in new_nodes:
            existing = Node.get_by_name(node_data["name"])
            if not existing:
                node = Node(
                    name=node_data["name"],
                    ip=node_data["ip"],
                    model=node_data["model"].lower(),
                    protocol=node_data["protocol"],
                    port=int(node_data["port"]),
                    username=node_data["username"],
                    password=node_data["password"],
                )
                node.save()

        # Sync to CSV for Oxidized
        all_nodes = Node.get_all()
        write_nodes_csv([n.to_dict() for n in all_nodes])
        reload_oxidized_nodes()

        return jsonify({"success": True, "count": len(new_nodes)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
