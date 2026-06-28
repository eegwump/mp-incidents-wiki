"""
Flask web server for Slack bot and webhook integration
Run with: python src/app.py
"""
import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from incident_manager import IncidentManager

load_dotenv()

app = Flask(__name__)
manager = IncidentManager()

# Slack client
slack_token = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=slack_token) if slack_token else None


@app.route("/", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "Incident Wiki"}), 200


@app.route("/api/incidents", methods=["GET"])
def list_incidents():
    """List all incidents."""
    incidents = manager.get_all_incidents()
    return jsonify({
        "count": len(incidents),
        "incidents": [
            {
                "id": incident_id,
                "name": incident.get("name"),
                "severity": incident.get("severity"),
                "description": incident.get("description")
            }
            for incident_id, incident in incidents.items()
        ]
    }), 200


@app.route("/api/incidents/<incident_id>", methods=["GET"])
def get_incident(incident_id):
    """Get specific incident details."""
    incident = manager.get_incident(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404
    
    return jsonify(incident), 200


@app.route("/api/search", methods=["GET"])
def search_incidents():
    """Search incidents."""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Missing search query"}), 400
    
    results = manager.search(query)
    return jsonify({
        "query": query,
        "count": len(results),
        "results": [
            {
                "id": result.get("id"),
                "name": result.get("name"),
                "severity": result.get("severity")
            }
            for result in results
        ]
    }), 200


@app.route("/api/slack/alert", methods=["POST"])
def slack_alert():
    """
    Trigger a Slack alert for an incident.
    
    POST body:
    {
        "incident_id": "db-connection-timeout",
        "channel": "#incidents"
    }
    """
    if not slack_client:
        return jsonify({"error": "Slack not configured"}), 503
    
    data = request.json
    incident_id = data.get("incident_id")
    channel = data.get("channel")
    
    if not incident_id:
        return jsonify({"error": "Missing incident_id"}), 400
    
    incident = manager.get_incident(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404
    
    try:
        from slack_handler import SlackIncidentHandler
        handler = SlackIncidentHandler()
        success = handler.send_incident_alert(incident_id, channel)
        
        if success:
            return jsonify({"status": "sent", "incident_id": incident_id}), 200
        else:
            return jsonify({"error": "Failed to send alert"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/email/alert", methods=["POST"])
def email_alert():
    """
    Trigger an email alert for an incident.
    
    POST body:
    {
        "incident_id": "db-connection-timeout",
        "recipients": ["team@example.com", "oncall@example.com"]
    }
    """
    data = request.json
    incident_id = data.get("incident_id")
    recipients = data.get("recipients")
    
    if not incident_id:
        return jsonify({"error": "Missing incident_id"}), 400
    
    incident = manager.get_incident(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404
    
    try:
        from email_handler import EmailHandler
        handler = EmailHandler()
        success = handler.send_incident_alert(incident_id, recipients)
        
        if success:
            return jsonify({"status": "sent", "incident_id": incident_id}), 200
        else:
            return jsonify({"error": "Failed to send alert"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/incident", methods=["POST"])
def incident_webhook():
    """
    Webhook to receive incident alerts from monitoring systems.
    
    POST body:
    {
        "incident_id": "db-connection-timeout",
        "severity": "critical",
        "message": "Database timeout detected"
    }
    """
    data = request.json
    incident_id = data.get("incident_id")
    
    if not incident_id:
        return jsonify({"error": "Missing incident_id"}), 400
    
    incident = manager.get_incident(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404
    
    # Send to Slack if configured
    if slack_client and incident.get("slack_notification"):
        try:
            from slack_handler import SlackIncidentHandler
            handler = SlackIncidentHandler()
            
            # Get channels from incident config
            channels = incident.get("notify_channels", ["incidents"])
            for channel in channels:
                handler.send_incident_alert(incident_id, channel)
        except Exception as e:
            print(f"Error sending Slack alert: {e}")
    
    return jsonify({
        "status": "received",
        "incident_id": incident_id,
        "incident_name": incident.get("name")
    }), 200


@app.route("/docs", methods=["GET"])
def docs():
    """API documentation."""
    return jsonify({
        "service": "Incident Wiki API",
        "endpoints": {
            "GET /": "Health check",
            "GET /api/incidents": "List all incidents",
            "GET /api/incidents/<id>": "Get incident details",
            "GET /api/search?q=query": "Search incidents",
            "POST /api/slack/alert": "Send Slack alert",
            "POST /webhook/incident": "Receive incident webhook",
            "GET /docs": "This documentation"
        },
        "examples": {
            "list": "curl http://localhost:5000/api/incidents",
            "search": "curl 'http://localhost:5000/api/search?q=database'",
            "alert": "curl -X POST http://localhost:5000/api/slack/alert -H 'Content-Type: application/json' -d '{\"incident_id\": \"db-connection-timeout\"}'",
            "webhook": "curl -X POST http://localhost:5000/webhook/incident -H 'Content-Type: application/json' -d '{\"incident_id\": \"db-connection-timeout\"}'"
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Starting Incident Wiki API on port {port}")
    print(f"📖 Docs available at http://localhost:{port}/docs")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
