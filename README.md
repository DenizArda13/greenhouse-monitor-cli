# Greenhouse IoT Monitor CLI

A Python CLI application to track temperatures in flower rooms of a greenhouse. Set ideal temperatures for each room and receive alerts when temperatures deviate by 5°C or more.

## Features

- Add flower rooms with ideal temperature settings
- Update current temperature readings for each room
- Automatic alerts when temperature deviates ±5°C from ideal
- List all rooms with their status
- Quick status overview
- Remove rooms

## Installation

### Prerequisites
- Python 3.7+

### Setup

```bash
# No external dependencies required - uses Python standard library only

# Make the script executable (optional)
chmod +x greenhouse.py
```

## Usage

### Add a Flower Room

```bash
python greenhouse.py add-room <room_name> <ideal_temperature>
```

Example:
```bash
python greenhouse.py add-room "Rose Room" 22.0
```

### Update Room Temperature

```bash
python greenhouse.py update-temp <room_id> <current_temperature>
```

Example:
```bash
python greenhouse.py update-temp abc12345 25.5
```

### List All Rooms

```bash
python greenhouse.py list-rooms
```

This shows:
- Room name
- Ideal temperature
- Current temperature
- Status (OK, ALERT, or No reading)
- Any active alerts

### Check for Alerts

```bash
python greenhouse.py check-alerts
```

Displays all rooms with temperature alerts (±5°C from ideal).

### Show Quick Status

```bash
python greenhouse.py status
```

Shows a summary of total rooms, rooms with readings, and active alerts.

### Remove a Room

```bash
python greenhouse.py remove-room <room_id>
```

Example:
```bash
python greenhouse.py remove-room abc12345
```

### Get Help

```bash
python greenhouse.py --help
python greenhouse.py <command> --help
```

## Test Commands

Here are commands to test the application:

### 1. Basic Setup Test

```bash
# Add multiple rooms
python greenhouse.py add-room "Rose Room" 22.0
python greenhouse.py add-room "Orchid Room" 24.5
python greenhouse.py add-room "Tulip Room" 20.0

# List rooms to see IDs
python greenhouse.py list-rooms
```

### 2. Temperature Update Test

```bash
# Get the room IDs from the list output, then update temperatures
# Replace <room_id_1>, <room_id_2>, <room_id_3> with actual IDs

# Normal temperature (should be OK)
python greenhouse.py update-temp <room_id_1> 22.0

# Slightly above ideal (should be OK, within 5°C)
python greenhouse.py update-temp <room_id_2> 26.0

# Trigger alert (6°C above ideal)
python greenhouse.py update-temp <room_id_3> 26.0
```

### 3. Alert System Test

```bash
# Add a test room with ideal temp 20°C
python greenhouse.py add-room "Alert Test Room" 20.0

# Get the room ID
python greenhouse.py list-rooms

# Test various temperature scenarios (replace <test_room_id> with actual ID):

# No alert - within range
python greenhouse.py update-temp <test_room_id> 21.0
python greenhouse.py check-alerts

# Alert triggered - 5°C above (exactly at threshold)
python greenhouse.py update-temp <test_room_id> 25.0
python greenhouse.py check-alerts

# Alert triggered - 6°C below
python greenhouse.py update-temp <test_room_id> 14.0
python greenhouse.py check-alerts

# Back to normal
python greenhouse.py update-temp <test_room_id> 20.0
python greenhouse.py check-alerts
```

### 4. Full Workflow Test

```bash
# Clean up any existing data
rm -f greenhouse_data.json

# Add rooms
python greenhouse.py add-room "Room A" 21.0
python greenhouse.py add-room "Room B" 23.0
python greenhouse.py add-room "Room C" 19.0

# Check status
python greenhouse.py status

# Get IDs and update temperatures
python greenhouse.py list-rooms

# (Replace IDs with actual values from list-rooms output)
python greenhouse.py update-temp <room_a_id> 21.0
python greenhouse.py update-temp <room_b_id> 29.0  # Should trigger alert
python greenhouse.py update-temp <room_c_id> 13.0  # Should trigger alert

# Check all rooms
python greenhouse.py list-rooms
python greenhouse.py check-alerts
python greenhouse.py status

# Clean up
python greenhouse.py remove-room <room_a_id>
python greenhouse.py list-rooms
```

### 5. Edge Case Tests

```bash
# Test with decimal temperatures
python greenhouse.py add-room "Precision Test" 22.5
python greenhouse.py list-rooms
# Get the ID
python greenhouse.py update-temp <id> 27.5  # Exactly 5.0 difference
python greenhouse.py check-alerts

# Test room name with spaces (use quotes)
python greenhouse.py add-room "North Wing Orchid Section" 24.0

# Test error handling - invalid room ID
python greenhouse.py update-temp invalid_id 25.0

# Test error handling - room not found
python greenhouse.py remove-room nonexistent
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
├── greenhouse.py    # Main CLI application
├── models.py        # Room data model
├── storage.py       # JSON storage handler
├── README.md        # This file
└── greenhouse_data.json  # Data file (created automatically)
```

