#!/usr/bin/env python3
"""Mock temperature server for the Greenhouse Monitor CLI.

Generates random temperature changes for all rooms every 2 seconds.
Temperature changes by -1, 0, or +1 degree Celsius randomly.
"""

import random
import time
import signal
import sys
from storage import Storage


class MockTemperatureServer:
    """Mock server that simulates temperature changes in flower rooms."""

    def __init__(self, interval: float = 2.0):
        self.storage = Storage()
        self.interval = interval
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\n🛑 Shutting down temperature server...")
        self.running = False

    def _update_temperatures(self) -> dict:
        """Update temperatures for all rooms randomly.

        Returns:
            dict: Mapping of room names to their temperature changes
        """
        rooms = self.storage.get_all_rooms()
        changes = {}

        for room in rooms:
            # Generate random change: -1, 0, or +1
            change = random.choice([-1.0, 0.0, 1.0])

            if room.current_temp is None:
                # Initialize with ideal temperature + small random variation
                new_temp = room.ideal_temp + random.uniform(-2.0, 2.0)
            else:
                new_temp = room.current_temp + change

            room.current_temp = round(new_temp, 1)
            self.storage.update_room(room)

            if change != 0:
                changes[room.name] = {
                    'old': round(room.current_temp - change, 1),
                    'new': room.current_temp,
                    'change': change
                }

        return changes

    def _check_alerts(self) -> list:
        """Check for rooms with temperature alerts.

        Returns:
            list: List of alert messages
        """
        rooms = self.storage.get_all_rooms()
        alerts = []

        for room in rooms:
            alert_msg = room.get_alert_message()
            if alert_msg:
                alerts.append(alert_msg)

        return alerts

    def run(self) -> None:
        """Run the mock temperature server."""
        print("🌡️  Mock Temperature Server Started")
        print(f"⏱️  Update interval: {self.interval} seconds")
        print("📝 Temperature changes by -1, 0, or +1°C randomly")
        print("🛑 Press Ctrl+C to stop\n")

        self.running = True
        iteration = 0

        while self.running:
            iteration += 1
            timestamp = time.strftime("%H:%M:%S")

            # Update temperatures
            changes = self._update_temperatures()

            # Display update
            print(f"[{timestamp}] Update #{iteration}")

            if changes:
                for room_name, change_info in changes.items():
                    direction = "↑" if change_info['change'] > 0 else "↓"
                    print(f"  {direction} {room_name}: {change_info['old']}°C → {change_info['new']}°C")
            else:
                print("  (no temperature changes)")

            # Check and display alerts
            alerts = self._check_alerts()
            if alerts:
                print("  ⚠️  ALERTS:")
                for alert in alerts:
                    print(f"     🚨 {alert}")

            print()

            # Wait for next interval
            try:
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break

        print("✅ Temperature server stopped.")


def main():
    """Main entry point for the mock server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Mock Temperature Server for Greenhouse Monitor"
    )
    parser.add_argument(
        '--interval', '-i',
        type=float,
        default=2.0,
        help='Update interval in seconds (default: 2.0)'
    )

    args = parser.parse_args()

    server = MockTemperatureServer(interval=args.interval)
    server.run()


if __name__ == '__main__':
    main()
