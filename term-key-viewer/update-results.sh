#!/bin/sh

SCRIPT_PATH=$(dirname "$(realpath "$0")")

jq -s . "$SCRIPT_PATH/../"term-key-survey-*.json > "$SCRIPT_PATH/src/results.json"
