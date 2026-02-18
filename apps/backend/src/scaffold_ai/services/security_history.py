"""Security score history tracking service."""

from typing import Dict, List
from datetime import datetime


class SecurityHistoryService:
    """Tracks security score improvements over time."""

    def __init__(self):
        self._history = {}  # {architecture_id: [scores]}

    def record_score(self, architecture_id: str, score: int, issues: List[Dict]) -> None:
        """Record a security score for an architecture."""
        if architecture_id not in self._history:
            self._history[architecture_id] = []

        self._history[architecture_id].append({
            "score": score,
            "timestamp": datetime.utcnow().isoformat(),
            "critical_count": sum(1 for i in issues if i.get("severity") == "critical"),
            "high_count": sum(1 for i in issues if i.get("severity") == "high"),
            "medium_count": sum(1 for i in issues if i.get("severity") == "medium"),
        })

    def get_history(self, architecture_id: str) -> List[Dict]:
        """Get security score history for an architecture."""
        return self._history.get(architecture_id, [])

    def get_improvement(self, architecture_id: str) -> Dict:
        """Calculate improvement metrics."""
        history = self._history.get(architecture_id, [])
        
        if len(history) < 2:
            return {"improvement": 0, "trend": "insufficient_data"}

        first_score = history[0]["score"]
        latest_score = history[-1]["score"]
        improvement = latest_score - first_score

        return {
            "improvement": improvement,
            "first_score": first_score,
            "latest_score": latest_score,
            "trend": "improving" if improvement > 0 else "declining" if improvement < 0 else "stable",
            "data_points": len(history),
        }
