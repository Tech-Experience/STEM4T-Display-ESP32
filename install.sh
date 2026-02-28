#!/usr/bin/env bash
#
# install.sh - Transfer all .py files to the T-Display ESP32 via ampy
#
# Usage:
#   ./install.sh              # auto-detect serial port
#   ./install.sh /dev/ttyUSB1 # specify port
#   ./install.sh --dry-run    # show what would be transferred
#

set -euo pipefail

BAUD=115200
DRY_RUN=false
PORT=""

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [PORT]"
            echo ""
            echo "Transfer all .py files to the T-Display ESP32."
            echo ""
            echo "  PORT       Serial port (auto-detected if omitted)"
            echo "  --dry-run  Show what would be transferred without sending"
            exit 0
            ;;
        *) PORT="$arg" ;;
    esac
done

# Auto-detect serial port if not specified
if [ -z "$PORT" ]; then
    for candidate in /dev/ttyUSB* /dev/ttyACM* /dev/serial/by-id/*; do
        if [ -e "$candidate" ]; then
            PORT="$candidate"
            break
        fi
    done
    if [ -z "$PORT" ]; then
        echo "ERROR: No serial port found. Connect the device or specify a port."
        exit 1
    fi
fi

echo "Port:  $PORT"
echo "Baud:  $BAUD"
echo ""

AMPY="pipenv run ampy --port $PORT --baud $BAUD"

# Gather all .py files in the project directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FILES=("$SCRIPT_DIR"/*.py)

if [ ${#FILES[@]} -eq 0 ]; then
    echo "No .py files found."
    exit 1
fi

echo "Files to transfer: ${#FILES[@]}"
echo "---"

SUCCESS=0
FAIL=0

for f in "${FILES[@]}"; do
    name="$(basename "$f")"
    if $DRY_RUN; then
        echo "  [dry-run] $name"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -n "  $name ... "
        if $AMPY put "$f"; then
            echo "OK"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "FAILED"
            FAIL=$((FAIL + 1))
        fi
    fi
done

echo "---"
echo "Done: $SUCCESS transferred, $FAIL failed."

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
