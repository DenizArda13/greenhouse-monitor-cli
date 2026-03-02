"""Data models for the Greenhouse Monitor CLI."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Room:
    """Represents a flower room in the greenhouse."""
    id: str
    name: str
    ideal_temp: float
    plant_name: str = ""
    current_temp: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert room to dictionary for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        """Create a Room from a dictionary."""
        return cls(**data)

    def get_temp_difference(self) -> Optional[float]:
        """Calculate the difference between current and ideal temperature."""
        if self.current_temp is None:
            return None
        return self.current_temp - self.ideal_temp

    def is_alert_triggered(self, threshold: float = 5.0) -> bool:
        """Check if temperature alert should be triggered."""
        diff = self.get_temp_difference()
        if diff is None:
            return False
        return abs(diff) >= threshold

    def get_alert_message(self, threshold: float = 5.0) -> Optional[str]:
        """Get alert message if temperature is out of range."""
        if not self.is_alert_triggered(threshold):
            return None

        diff = self.get_temp_difference()
        if diff > 0:
            return f"ALERT: Room '{self.name}' is {diff:.1f}°C ABOVE ideal temperature!"
        else:
            return f"ALERT: Room '{self.name}' is {abs(diff):.1f}°C BELOW ideal temperature!"
