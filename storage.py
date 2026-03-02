"""Storage module for the Greenhouse Monitor CLI."""
import json
import os
from typing import List, Optional
from models import Room


DATA_FILE = "greenhouse_data.json"


class Storage:
    """Handles persistence of room data."""

    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file

    def _load_data(self) -> dict:
        """Load data from JSON file."""
        if not os.path.exists(self.data_file):
            return {"rooms": []}
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"rooms": []}

    def _save_data(self, data: dict) -> None:
        """Save data to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_all_rooms(self) -> List[Room]:
        """Get all rooms from storage."""
        data = self._load_data()
        return [Room.from_dict(room_data) for room_data in data.get("rooms", [])]

    def get_room_by_id(self, room_id: str) -> Optional[Room]:
        """Get a specific room by ID."""
        rooms = self.get_all_rooms()
        for room in rooms:
            if room.id == room_id:
                return room
        return None

    def get_room_by_name(self, name: str) -> Optional[Room]:
        """Get a specific room by name (case-insensitive)."""
        normalized_name = name.strip().lower()
        rooms = self.get_all_rooms()
        for room in rooms:
            if room.name.strip().lower() == normalized_name:
                return room
        return None

    def add_room(self, room: Room) -> None:
        """Add a new room to storage."""
        data = self._load_data()
        data["rooms"].append(room.to_dict())
        self._save_data(data)

    def update_room(self, room: Room) -> bool:
        """Update an existing room."""
        data = self._load_data()
        for i, room_data in enumerate(data.get("rooms", [])):
            if room_data["id"] == room.id:
                data["rooms"][i] = room.to_dict()
                self._save_data(data)
                return True
        return False

    def remove_room(self, room_id: str) -> bool:
        """Remove a room by ID."""
        data = self._load_data()
        original_count = len(data.get("rooms", []))
        data["rooms"] = [r for r in data.get("rooms", []) if r["id"] != room_id]
        if len(data["rooms"]) < original_count:
            self._save_data(data)
            return True
        return False

    def clear_all_rooms(self) -> None:
        """Clear all rooms from storage."""
        self._save_data({"rooms": []})
