#!/bin/sh
jq -s . ../term-key-survey-*.json > src/results.json
