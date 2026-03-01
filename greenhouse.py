#!/usr/bin/env python3
"""Greenhouse Monitor CLI - Track temperatures in flower rooms."""

import argparse
import os
import signal
import sys
import time
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
    CLEAR = '\033[2J\033[H'  # Clear screen and move cursor to top

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
        self.monitoring = False

    def add_room(self, name: str, ideal_temp: float) -> None:
        """Add a new flower room with ideal temperature."""
        if self.storage.get_room_by_name(name):
            print(f"✗ Room '{name}' already exists.", file=sys.stderr)
            return

        room = Room(
            id=str(uuid.uuid4())[:8],
            name=name,
            ideal_temp=ideal_temp,
            current_temp=None
        )
        self.storage.add_room(room)
        print(f"✓ Added room '{name}' with ideal temperature {ideal_temp}°C")

    def update_temp(self, room_name: str, current_temp: float) -> None:
        """Update the current temperature of a room."""
        room = self.storage.get_room_by_name(room_name)

        if not room:
            print(f"✗ Room '{room_name}' not found.", file=sys.stderr)
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

            alert_msg = room.get_alert_message()
            if alert_msg:
                print(Colors.red(f"  → {alert_msg}"))

        print("=" * 70 + "\n")

    def remove_room(self, room_name: str) -> None:
        """Remove a flower room by name."""
        room = self.storage.get_room_by_name(room_name)

        if not room:
            print(f"✗ Room '{room_name}' not found.", file=sys.stderr)
            return

        if self.storage.remove_room(room.id):
            print(f"✓ Removed room '{room.name}'")
        else:
            print(f"✗ Failed to remove room '{room.name}'.", file=sys.stderr)

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

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.monitoring = False

    def monitor(self, interval: float = 2.0) -> None:
        """Continuously monitor all rooms in a live loop.

        Args:
            interval: Refresh interval in seconds
        """
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)

        rooms = self.storage.get_all_rooms()
        if not rooms:
            print("No rooms configured. Use 'add-room' to add rooms first.")
            return

        self.monitoring = True

        # Store interval for display
        display_interval = interval

        print("🖥️  Live Monitor Started")
        print(f"⏱️  Refresh interval: {display_interval} seconds")
        print("🛑 Press Ctrl+C to stop\n")

        # Give user time to read the message before clearing screen
        time.sleep(1)

        while self.monitoring:
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')

            # Get fresh data
            rooms = self.storage.get_all_rooms()
            timestamp = time.strftime("%H:%M:%S")

            # Header
            print(Colors.CLEAR, end="")
            print("=" * 70)
            print(f"🌡️  GREENHOUSE LIVE MONITOR - {timestamp}")
            print("=" * 70)
            print()

            # Status summary
            total_rooms = len(rooms)
            rooms_with_reading = sum(1 for r in rooms if r.current_temp is not None)
            alert_count = sum(1 for r in rooms if r.is_alert_triggered())

            print(f"Total Rooms: {total_rooms} | With Readings: {rooms_with_reading}", end="")
            if alert_count > 0:
                print(f" | {Colors.bold_red(f'ALERTS: {alert_count}')}")
            else:
                print(f" | {Colors.green('All OK')}")
            print("-" * 70)

            # Room details
            for room in rooms:
                current = f"{room.current_temp}°C" if room.current_temp is not None else "N/A"

                if room.is_alert_triggered():
                    status = Colors.red("⚠ ALERT")
                    alert_indicator = " 🚨"
                elif room.current_temp is None:
                    status = Colors.yellow("No reading")
                    alert_indicator = ""
                else:
                    diff = room.get_temp_difference()
                    status = Colors.green(f"OK ({diff:+.1f}°C)")
                    alert_indicator = ""

                print(f"{room.name:<20} Ideal: {room.ideal_temp:<6} Current: {current:<8} {status}{alert_indicator}")

                alert_msg = room.get_alert_message()
                if alert_msg:
                    print(Colors.red(f"  → {alert_msg}"))

            print("-" * 70)
            print(f"🔄 Refreshing every {display_interval}s | Press Ctrl+C to exit")

            # Wait for next refresh
            try:
                time.sleep(interval)
            except KeyboardInterrupt:
                self.monitoring = False
                break

        # Clear the line to remove any ^C characters
        print("\r" + " " * 50 + "\r", end="")
        print("✅ Live monitor stopped.")


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
    update_parser.add_argument('room_name', help='Room name')
    update_parser.add_argument('current_temp', type=float, help='Current temperature in Celsius')

    # list-rooms command
    subparsers.add_parser('list-rooms', help='List all rooms and their status')

    # remove-room command
    remove_parser = subparsers.add_parser('remove-room', help='Remove a room')
    remove_parser.add_argument('room_name', help='Room name to remove')

    # check-alerts command
    subparsers.add_parser('check-alerts', help='Check all rooms for temperature alerts')

    # status command
    subparsers.add_parser('status', help='Show quick status overview')

    # monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Live monitor with continuous updates')
    monitor_parser.add_argument(
        '--interval', '-i',
        type=float,
        default=2.0,
        help='Refresh interval in seconds (default: 2.0)'
    )

    args = parser.parse_args()

    if args.command == 'add-room':
        cli.add_room(args.name, args.ideal_temp)
    elif args.command == 'update-temp':
        cli.update_temp(args.room_name, args.current_temp)
    elif args.command == 'list-rooms':
        cli.list_rooms()
    elif args.command == 'remove-room':
        cli.remove_room(args.room_name)
    elif args.command == 'check-alerts':
        cli.check_alerts()
    elif args.command == 'status':
        cli.status()
    elif args.command == 'monitor':
        cli.monitor(args.interval)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
