"""
Slack Bot Handler - Send incident information to Slack
"""
import os
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from incident_manager import IncidentManager

load_dotenv()


class SlackIncidentHandler:
    def __init__(self):
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        if not bot_token:
            raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
        
        self.client = WebClient(token=bot_token)
        self.manager = IncidentManager()
    
    def send_incident_alert(self, incident_id: str, channel: Optional[str] = None) -> bool:
        """
        Send incident information to Slack channel.
        
        Args:
            incident_id: ID of the incident to send
            channel: Optional channel override (defaults to #incidents)
        """
        incident = self.manager.get_incident(incident_id)
        if not incident:
            print(f"❌ Incident '{incident_id}' not found")
            return False
        
        channel = channel or os.getenv("INCIDENTS_CHANNEL", "incidents")
        
        try:
            blocks = self._format_incident_blocks(incident)
            response = self.client.chat_postMessage(
                channel=channel,
                text=f"🚨 Incident Alert: {incident.get('name')}",
                blocks=blocks
            )
            print(f"✅ Message sent to {channel}")
            return True
        except SlackApiError as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def _format_incident_blocks(self, incident: dict) -> list:
        """Format incident data as Slack message blocks."""
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        severity = incident.get("severity", "unknown").lower()
        emoji = severity_emoji.get(severity, "⚫")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {incident.get('name', 'Incident Alert')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*SLA:*\n{incident.get('resolution_time_sla', 'N/A')} min"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{incident.get('description', 'N/A')}"
                }
            }
        ]
        
        # Add triggers
        triggers = incident.get("triggers", [])
        if triggers:
            trigger_text = "*Triggers:*\n" + "\n".join(f"• {t}" for t in triggers[:5])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": trigger_text
                }
            })
        
        # Add quick actions
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Quick Actions:*\n• Check runbook\n• Contact on-call\n• Start incident"
            }
        })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        # Add runbook preview
        runbook = incident.get("runbook", "")
        if runbook:
            runbook_preview = runbook[:500] + "..." if len(runbook) > 500 else runbook
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Runbook Preview:*\n```{runbook_preview}```"
                }
            })
        
        return blocks
    
    def send_search_results(self, query: str, channel: Optional[str] = None) -> bool:
        """Search incidents and send matching results to Slack."""
        results = self.manager.search(query)
        
        if not results:
            try:
                self.client.chat_postMessage(
                    channel=channel or os.getenv("INCIDENTS_CHANNEL", "incidents"),
                    text=f"No incidents found matching '{query}'"
                )
            except SlackApiError as e:
                print(f"❌ Error: {e}")
            return False
        
        channel = channel or os.getenv("INCIDENTS_CHANNEL", "incidents")
        
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🔍 Search Results for '{query}'"
                    }
                }
            ]
            
            # Add each result as a section
            for incident in results[:10]:  # Limit to 10 results
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{incident.get('name')}* (ID: `{incident.get('id')}`)\n{incident.get('description', 'N/A')}"
                    }
                })
                blocks.append({"type": "divider"})
            
            self.client.chat_postMessage(
                channel=channel,
                text=f"Search results for '{query}'",
                blocks=blocks
            )
            print(f"✅ Sent {len(results)} search results to {channel}")
            return True
        except SlackApiError as e:
            print(f"❌ Error sending search results: {e}")
            return False


if __name__ == "__main__":
    # Example usage (requires SLACK_BOT_TOKEN in .env)
    try:
        handler = SlackIncidentHandler()
        
        # Send specific incident
        # handler.send_incident_alert("db-connection-timeout")
        
        # Search and send results
        # handler.send_search_results("database")
        
        print("✅ Slack handler initialized successfully")
    except ValueError as e:
        print(f"⚠️  {e}")
        print("Set SLACK_BOT_TOKEN in .env file to enable Slack integration")
