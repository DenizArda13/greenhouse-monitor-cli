# Greenhouse IoT Monitor CLI

A Python CLI application to track temperatures in flower rooms of a greenhouse. Set ideal temperatures for each room and receive alerts when temperatures deviate by 5°C or more.

## Features

- Add flower rooms with ideal temperature settings
- Update current temperature readings for each room
- Automatic alerts when temperature deviates ±5°C from ideal
- List all rooms with their status
- Quick status overview
- Remove rooms
- **Mock temperature server** that simulates real-time temperature changes
- **Live monitor** with continuous updates and real-time alerts

## Installation

### Prerequisites
- Python 3.7+

### Setup

```bash
# No external dependencies required - uses Python standard library only

# Make the scripts executable (optional)
chmod +x greenhouse.py
chmod +x mock_server.py
```

## Usage

### Add a Flower Room

```bash
python3 greenhouse.py add-room <room_name> <ideal_temperature>
```

Example:
```bash
python3 greenhouse.py add-room "Rose Room" 22.0
```

### Update Room Temperature

```bash
python3 greenhouse.py update-temp <room_name> <current_temperature>
```

Example:
```bash
python3 greenhouse.py update-temp "Rose Room" 25.5
```

### List All Rooms

```bash
python3 greenhouse.py list-rooms
```

This shows:
- Room name
- Ideal temperature
- Current temperature
- Status (OK, ALERT, or No reading)
- Any active alerts

### Check for Alerts

```bash
python3 greenhouse.py check-alerts
```

Displays all rooms with temperature alerts (±5°C from ideal).

### Show Quick Status

```bash
python3 greenhouse.py status
```

Shows a summary of total rooms, rooms with readings, and active alerts.

### Remove a Room

```bash
python3 greenhouse.py remove-room <room_name>
```

Example:
```bash
python3 greenhouse.py remove-room "Rose Room"
```

### Live Monitor

Continuously monitor all rooms with real-time updates. The screen refreshes every few seconds showing current temperatures and alerts.

```bash
python3 greenhouse.py monitor
```

With custom refresh interval (default is 2 seconds):
```bash
python3 greenhouse.py monitor --interval 3
# or
python3 greenhouse.py monitor -i 1
```

Press `Ctrl+C` to stop the monitor.

### Mock Temperature Server

Run a mock server that automatically generates temperature changes for all rooms every 2 seconds. Temperature changes by -1, 0, or +1 degree Celsius randomly.

```bash
# Terminal 1: Start the mock server
python3 mock_server.py

# Terminal 2: In another terminal, monitor the changes
python3 greenhouse.py monitor
```

With custom update interval:
```bash
python3 mock_server.py --interval 3
# or
python3 mock_server.py -i 1
```

Press `Ctrl+C` to stop the server.

### Get Help

```bash
python3 greenhouse.py --help
python3 greenhouse.py <command> --help
python3 mock_server.py --help
```

## Test Commands

Here are commands to test the application:

### 1. Basic Setup Test

```bash
# Add multiple rooms
python3 greenhouse.py add-room "Rose Room" 22.0
python3 greenhouse.py add-room "Orchid Room" 24.5
python3 greenhouse.py add-room "Tulip Room" 20.0

# List rooms
python3 greenhouse.py list-rooms
```

### 2. Temperature Update Test

```bash
# Update temperatures by room name

# Normal temperature (should be OK)
python3 greenhouse.py update-temp "Rose Room" 22.0

# Slightly above ideal (should be OK, within 5°C)
python3 greenhouse.py update-temp "Orchid Room" 26.0

# Trigger alert (6°C above ideal)
python3 greenhouse.py update-temp "Tulip Room" 26.0
```

### 3. Alert System Test

```bash
# Add a test room with ideal temp 20°C
python3 greenhouse.py add-room "Alert Test Room" 20.0

# Test various temperature scenarios:

# No alert - within range
python3 greenhouse.py update-temp "Alert Test Room" 21.0
python3 greenhouse.py check-alerts

# Alert triggered - 5°C above (exactly at threshold)
python3 greenhouse.py update-temp "Alert Test Room" 25.0
python3 greenhouse.py check-alerts

# Alert triggered - 6°C below
python3 greenhouse.py update-temp "Alert Test Room" 14.0
python3 greenhouse.py check-alerts

# Back to normal
python3 greenhouse.py update-temp "Alert Test Room" 20.0
python3 greenhouse.py check-alerts
```

### 4. Live Monitor Test

```bash
# Add some rooms first
python3 greenhouse.py add-room "Live Test A" 22.0
python3 greenhouse.py add-room "Live Test B" 25.0

# Set initial temperatures
python3 greenhouse.py update-temp "Live Test A" 22.0
python3 greenhouse.py update-temp "Live Test B" 25.0

# Start the live monitor (press Ctrl+C to stop)
python3 greenhouse.py monitor

# Or with custom refresh interval
python3 greenhouse.py monitor --interval 1
```

### 5. Mock Server Test (Full Simulation)

Open two terminals:

**Terminal 1 - Start the mock server:**
```bash
# Clean up and setup
rm -f greenhouse_data.json
python3 greenhouse.py add-room "Rose Room" 22.0
python3 greenhouse.py add-room "Orchid Room" 24.5
python3 greenhouse.py add-room "Tulip Room" 20.0

# Start the mock temperature server
python3 mock_server.py
```

**Terminal 2 - Monitor in real-time:**
```bash
# Watch the temperatures change automatically
python3 greenhouse.py monitor

# Or check alerts periodically
python3 greenhouse.py check-alerts
```

### 6. Full Workflow Test

```bash
# Clean up any existing data
rm -f greenhouse_data.json

# Add rooms
python3 greenhouse.py add-room "Room A" 21.0
python3 greenhouse.py add-room "Room B" 23.0
python3 greenhouse.py add-room "Room C" 19.0

# Check status
python3 greenhouse.py status

# Update temperatures by room name
python3 greenhouse.py update-temp "Room A" 21.0
python3 greenhouse.py update-temp "Room B" 29.0  # Should trigger alert
python3 greenhouse.py update-temp "Room C" 13.0  # Should trigger alert

# Check all rooms
python3 greenhouse.py list-rooms
python3 greenhouse.py check-alerts
python3 greenhouse.py status

# Clean up
python3 greenhouse.py remove-room "Room A"
python3 greenhouse.py list-rooms
```

### 7. Edge Case Tests

```bash
# Test with decimal temperatures
python3 greenhouse.py add-room "Precision Test" 22.5
python3 greenhouse.py list-rooms
python3 greenhouse.py update-temp "Precision Test" 27.5  # Exactly 5.0 difference
python3 greenhouse.py check-alerts

# Test room name with spaces (use quotes)
python3 greenhouse.py add-room "North Wing Orchid Section" 24.0

# Test error handling - room not found
python3 greenhouse.py update-temp "Nonexistent Room" 25.0

# Test duplicate room prevention
python3 greenhouse.py add-room "Rose Room" 22.0
python3 greenhouse.py add-room "Rose Room" 22.0  # Should fail

# Test removal by name
python3 greenhouse.py remove-room "North Wing Orchid Section"
```

## Data Storage

Room data is stored in `greenhouse_data.json` in the current directory. This file is created automatically when you add your first room.

## Alert Threshold

The default alert threshold is **5°C**. An alert is triggered when:
- Current temperature ≥ Ideal temperature + 5°C (too hot)
- Current temperature ≤ Ideal temperature - 5°C (too cold)

## Project Structure

```
greenhouse-monitor-cli/
├── greenhouse.py      # Main CLI application
├── mock_server.py     # Mock temperature server
├── models.py          # Room data model
├── storage.py         # JSON storage handler
├── README.md          # This file
└── greenhouse_data.json  # Data file (created automatically)
```

## How It Works

### Mock Server
The `mock_server.py` script simulates a real IoT temperature sensor system:
- Reads all rooms from storage
- Every 2 seconds, randomly changes each room's temperature by -1, 0, or +1°C
- Saves updated temperatures back to storage
- Displays changes and alerts in real-time

### Live Monitor
The `monitor` command provides a dashboard-like experience:
- Clears the screen and displays current status
- Refreshes at specified intervals (default 2 seconds)
- Shows room names, ideal temps, current temps, and status
- Highlights alerts in red with warning symbols
- Press Ctrl+C to exit

### Typical Workflow
1. Add rooms with ideal temperatures using `add-room`
2. Start the mock server in one terminal: `python3 mock_server.py`
3. Start the live monitor in another terminal: `python3 greenhouse.py monitor`
4. Watch temperatures change and alerts trigger automatically!

