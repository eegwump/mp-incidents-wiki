import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.incident_manager import IncidentManager


class IncidentManagerTests(unittest.TestCase):
    def test_defaults_to_team_incidents_folder(self):
        manager = IncidentManager()
        self.assertIn(
            "pending-bo-withdrawals-no-batch-created-p2",
            manager.list_all(),
        )
        self.assertTrue(manager.incidents_dir.exists())

    def test_resolves_incident_by_partial_name_prefix(self):
        manager = IncidentManager()
        incident = manager.resolve_incident("pending-bo-settlements")
        self.assertEqual(
            incident.get("id"),
            "pending-bo-withdrawals-no-batch-created-p2",
        )


if __name__ == "__main__":
    unittest.main()
