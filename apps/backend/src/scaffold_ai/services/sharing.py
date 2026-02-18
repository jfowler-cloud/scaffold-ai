"""Architecture sharing service for collaboration."""

import json
import hashlib
from typing import Dict, Optional


class SharingService:
    """Manages architecture sharing via unique URLs."""

    def __init__(self):
        self._shared_architectures = {}  # In-memory store (use DB in production)

    def create_share_link(self, graph: Dict, title: str = "Shared Architecture") -> str:
        """Create a shareable link for an architecture."""
        from datetime import datetime
        
        # Generate unique ID from graph content
        graph_json = json.dumps(graph, sort_keys=True)
        share_id = hashlib.sha256(graph_json.encode()).hexdigest()[:12]

        # Store architecture
        self._shared_architectures[share_id] = {
            "graph": graph,
            "title": title,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        return share_id

    def get_shared_architecture(self, share_id: str) -> Optional[Dict]:
        """Retrieve a shared architecture by ID."""
        return self._shared_architectures.get(share_id)

    def list_shared(self) -> list:
        """List all shared architectures (for admin/debugging)."""
        return [
            {
                "id": share_id,
                "title": data["title"],
                "node_count": len(data["graph"].get("nodes", [])),
                "created_at": data["created_at"],
            }
            for share_id, data in self._shared_architectures.items()
        ]
