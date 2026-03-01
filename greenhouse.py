#!/usr/bin/env python3
"""Greenhouse Monitor CLI - Track temperatures in flower rooms."""

import argparse
import sys
import uuid
from typing import Optional, List
from models import Room
from storage import Storage


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @classmethod
    def red(cls, text: str) -> str:
        return f"{cls.RED}{text}{cls.END}"

    @classmethod
    def green(cls, text: str) -> str:
        return f"{cls.GREEN}{text}{cls.END}"

    @classmethod
    def yellow(cls, text: str) -> str:
        return f"{cls.YELLOW}{text}{cls.END}"

    @classmethod
    def bold_red(cls, text: str) -> str:
        return f"{cls.BOLD}{cls.RED}{text}{cls.END}"


class GreenhouseCLI:
    """Main CLI application for greenhouse monitoring."""

    def __init__(self):
        self.storage = Storage()

    def add_room(self, name: str, ideal_temp: float) -> None:
        """Add a new flower room with ideal temperature."""
        room = Room(
            id=str(uuid.uuid4())[:8],
            name=name,
            ideal_temp=ideal_temp,
            current_temp=None
        )
        self.storage.add_room(room)
        print(f"✓ Added room '{name}' with ideal temperature {ideal_temp}°C (ID: {room.id})")

    def update_temp(self, room_id: str, current_temp: float) -> None:
        """Update the current temperature of a room."""
        room = self.storage.get_room_by_id(room_id)

        if not room:
            print(f"✗ Room with ID '{room_id}' not found.", file=sys.stderr)
            return

        room.current_temp = current_temp
        self.storage.update_room(room)

        print(f"✓ Updated '{room.name}' temperature to {current_temp}°C")

        # Check for alerts
        alert_msg = room.get_alert_message()
        if alert_msg:
            print(Colors.bold_red(alert_msg))

    def list_rooms(self) -> None:
        """List all flower rooms and their status."""
        rooms = self.storage.get_all_rooms()

        if not rooms:
            print("No rooms configured. Use 'add-room' to add a room.")
            return

        print("\n" + "=" * 70)
        print(f"{'Room':<20} {'Ideal Temp':<12} {'Current':<12} {'Status':<20}")
        print("=" * 70)

        for room in rooms:
            current = f"{room.current_temp}°C" if room.current_temp is not None else "N/A"

            if room.is_alert_triggered():
                status = Colors.red("⚠ ALERT")
            elif room.current_temp is None:
                status = Colors.yellow("No reading")
            else:
                diff = room.get_temp_difference()
                status = Colors.green(f"OK ({diff:+.1f}°C)")

            print(f"{room.name:<20} {room.ideal_temp:<12} {current:<12} {status}")
            print(f"  ID: {room.id}")

            alert_msg = room.get_alert_message()
            if alert_msg:
                print(Colors.red(f"  → {alert_msg}"))

        print("=" * 70 + "\n")

    def remove_room(self, room_id: str) -> None:
        """Remove a flower room by ID."""
        room = self.storage.get_room_by_id(room_id)

        if not room:
            print(f"✗ Room with ID '{room_id}' not found.", file=sys.stderr)
            return

        if self.storage.remove_room(room_id):
            print(f"✓ Removed room '{room.name}' (ID: {room_id})")
        else:
            print(f"✗ Failed to remove room '{room_id}'.", file=sys.stderr)

    def check_alerts(self) -> None:
        """Check all rooms for temperature alerts."""
        rooms = self.storage.get_all_rooms()

        alerts_found = False

        for room in rooms:
            alert_msg = room.get_alert_message()
            if alert_msg:
                print(Colors.bold_red(alert_msg))
                alerts_found = True

        if not alerts_found:
            print(Colors.green("✓ All rooms are within acceptable temperature range."))

    def status(self) -> None:
        """Show quick status overview of all rooms."""
        rooms = self.storage.get_all_rooms()

        if not rooms:
            print("No rooms configured.")
            return

        total_rooms = len(rooms)
        rooms_with_reading = sum(1 for r in rooms if r.current_temp is not None)
        alert_count = sum(1 for r in rooms if r.is_alert_triggered())

        print("\n📊 Greenhouse Status Overview")
        print("-" * 30)
        print(f"Total Rooms: {total_rooms}")
        print(f"Rooms with readings: {rooms_with_reading}")

        if alert_count > 0:
            print(Colors.bold_red(f"Active Alerts: {alert_count}"))
        else:
            print(Colors.green("Active Alerts: 0"))

        print()


def main():
    """Main entry point for the CLI."""
    cli = GreenhouseCLI()

    parser = argparse.ArgumentParser(
        description="Greenhouse Monitor CLI - Track flower room temperatures."
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # add-room command
    add_parser = subparsers.add_parser('add-room', help='Add a new flower room')
    add_parser.add_argument('name', help='Name of the flower room')
    add_parser.add_argument('ideal_temp', type=float, help='Ideal temperature in Celsius')

    # update-temp command
    update_parser = subparsers.add_parser('update-temp', help='Update room temperature')
    update_parser.add_argument('room_id', help='Room ID')
    update_parser.add_argument('current_temp', type=float, help='Current temperature in Celsius')

    # list-rooms command
    subparsers.add_parser('list-rooms', help='List all rooms and their status')

    # remove-room command
    remove_parser = subparsers.add_parser('remove-room', help='Remove a room')
    remove_parser.add_argument('room_id', help='Room ID to remove')

    # check-alerts command
    subparsers.add_parser('check-alerts', help='Check all rooms for temperature alerts')

    # status command
    subparsers.add_parser('status', help='Show quick status overview')

    args = parser.parse_args()

    if args.command == 'add-room':
        cli.add_room(args.name, args.ideal_temp)
    elif args.command == 'update-temp':
        cli.update_temp(args.room_id, args.current_temp)
    elif args.command == 'list-rooms':
        cli.list_rooms()
    elif args.command == 'remove-room':
        cli.remove_room(args.room_id)
    elif args.command == 'check-alerts':
        cli.check_alerts()
    elif args.command == 'status':
        cli.status()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
