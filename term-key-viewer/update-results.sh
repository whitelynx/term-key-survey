#!/bin/sh
jq -sc . ../term-key-survey-*.json > src/results.json
