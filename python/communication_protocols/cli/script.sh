#!/bin/bash

# Check API_KEY
if [[ -z "$API_KEY" ]]; then
    echo "API_KEY is not set." >&2
    exit 1
fi

if [[ "$API_KEY" != "TEST" ]]; then
    echo "API_KEY value is not TEST." >&2
    exit 1
fi

# Parse --text argument
while [[ $# -gt 0 ]]; do
    case "$1" in
        --text)
            TEXT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [[ -z "$TEXT" ]]; then
    echo "No --text argument provided." >&2
    exit 1
fi

echo "$TEXT"
