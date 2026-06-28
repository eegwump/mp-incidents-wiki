"""
Incident Manager - Search and retrieve incidents from YAML files
"""
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class IncidentManager:
    def __init__(self, incidents_dir: Optional[str] = None):
        self.incidents_dir = self._resolve_incidents_dir(incidents_dir)
        self.incidents: Dict[str, Dict] = {}
        self.load_all_incidents()

    def _resolve_incidents_dir(self, incidents_dir: Optional[str]) -> Path:
        """Resolve the incident directory using the provided path, env override, or defaults."""
        candidates = []

        if incidents_dir:
            candidates.append(Path(incidents_dir))

        env_dir = os.getenv("INCIDENTS_DIR")
        if env_dir:
            candidates.append(Path(env_dir))

        candidates.extend([
            Path("merchant_settlement/incidents"),
            Path("incidents"),
        ])

        for candidate in candidates:
            if candidate.exists():
                return candidate

        if incidents_dir:
            return Path(incidents_dir)
        if env_dir:
            return Path(env_dir)
        return Path("merchant_settlement/incidents")
    
    def load_all_incidents(self) -> None:
        """Load all incident YAML files from the resolved incidents directory."""
        self.incidents.clear()

        if not self.incidents_dir.exists():
            print(f"Warning: incidents directory not found at {self.incidents_dir}")
            return
        
        for yaml_file in sorted(self.incidents_dir.rglob("*.yaml")):
            if not yaml_file.is_file():
                continue
            try:
                with open(yaml_file, "r") as f:
                    incident = yaml.safe_load(f)
                    if incident and "id" in incident:
                        self.incidents[incident["id"]] = incident
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
    
    def search(self, query: str) -> List[Dict]:
        """
        Search incidents by name, ID, aliases, or description.
        Returns list of matching incidents.
        """
        query_lower = query.lower()
        results = []
        
        for incident_id, incident in self.incidents.items():
            # Search in name
            if query_lower in incident.get("name", "").lower():
                results.append(incident)
                continue
            
            # Search in ID
            if query_lower in incident_id.lower():
                results.append(incident)
                continue
            
            # Search in aliases
            aliases = incident.get("aliases", [])
            if any(query_lower in alias.lower() for alias in aliases):
                results.append(incident)
                continue
            
            # Search in description
            if query_lower in incident.get("description", "").lower():
                results.append(incident)
                continue
        
        return results

    def _normalize_text(self, value: str) -> str:
        """Normalize text for flexible incident lookups."""
        return re.sub(r"[^a-z0-9]", "", value.lower())

    def _tokenize_text(self, value: str) -> List[str]:
        """Split text into normalized tokens for shorthand matching."""
        tokens = re.findall(r"[a-z0-9]+", value.lower())
        return [token[:-1] if len(token) > 3 and token.endswith("s") else token for token in tokens]

    def _matches_token_prefix(self, candidate: str, query: str) -> bool:
        """Check whether a candidate starts with the query token sequence."""
        candidate_tokens = self._tokenize_text(candidate)
        query_tokens = self._tokenize_text(query)

        if not candidate_tokens or not query_tokens or len(query_tokens) > len(candidate_tokens):
            return False

        return candidate_tokens[: len(query_tokens)] == query_tokens

    def resolve_incident(self, incident_id_or_query: str) -> Optional[Dict]:
        """Resolve an incident by exact ID, normalized prefix, or name shorthand."""
        if not incident_id_or_query:
            return None

        exact_match = self.get_incident(incident_id_or_query)
        if exact_match:
            return exact_match

        normalized_query = self._normalize_text(incident_id_or_query)
        if not normalized_query:
            return None

        exact_candidates = []
        prefix_candidates = []
        shorthand_candidates = []

        for incident_id, incident in self.incidents.items():
            candidate_values = [
                incident_id,
                incident.get("name", ""),
                incident.get("description", ""),
            ]
            candidate_values.extend(incident.get("aliases", []))

            normalized_candidates = [
                self._normalize_text(value)
                for value in candidate_values
                if value
            ]

            if normalized_query in normalized_candidates:
                exact_candidates.append(incident)
                continue

            if any(candidate.startswith(normalized_query) or normalized_query in candidate for candidate in normalized_candidates):
                prefix_candidates.append(incident)
                continue

            if any(
                self._matches_token_prefix(candidate, incident_id_or_query)
                for candidate in candidate_values
                if candidate
            ):
                shorthand_candidates.append(incident)

        if len(exact_candidates) == 1:
            return exact_candidates[0]

        if len(prefix_candidates) == 1:
            return prefix_candidates[0]

        if len(shorthand_candidates) == 1:
            return shorthand_candidates[0]

        if len(exact_candidates) > 1:
            return exact_candidates[0]

        if len(prefix_candidates) > 1:
            return prefix_candidates[0]

        if len(shorthand_candidates) > 1:
            return shorthand_candidates[0]

        return None
    
    def get_incident(self, incident_id: str) -> Optional[Dict]:
        """Get specific incident by ID."""
        return self.incidents.get(incident_id)
    
    def get_all_incidents(self) -> Dict[str, Dict]:
        """Get all incidents."""
        return self.incidents
    
    def get_incident_summary(self, incident: Dict) -> str:
        """Format incident as readable summary."""
        summary = f"""
📋 **{incident.get('name', 'Unknown')}** (ID: {incident.get('id', 'N/A')})
Severity: {incident.get('severity', 'unknown').upper()}

📝 Description:
{incident.get('description', 'N/A')}

🚨 Triggers:
"""
        for trigger in incident.get('triggers', []):
            summary += f"  • {trigger}\n"
        
        summary += f"\n⏱️  SLA: {incident.get('resolution_time_sla', 'N/A')} minutes\n"
        
        if incident.get('slack_notification'):
            summary += "\n🔔 Slack notification enabled\n"
        
        return summary
    
    def get_incident_runbook(self, incident: Dict) -> str:
        """Get the runbook for an incident."""
        return incident.get('runbook', 'No runbook available')
    
    def list_all(self) -> List[str]:
        """List all incident IDs."""
        return list(self.incidents.keys())


if __name__ == "__main__":
    # Example usage
    manager = IncidentManager()
    
    print("📚 Available Incidents:")
    for incident_id in manager.list_all():
        incident = manager.get_incident(incident_id)
        print(f"  • {incident_id}: {incident.get('name', 'Unknown')}")
    
    # Search example
    print("\n🔍 Search Results for 'database':")
    results = manager.search("database")
    for incident in results:
        print(manager.get_incident_summary(incident))
