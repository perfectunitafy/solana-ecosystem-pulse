#!/bin/bash
# Solana Pulse pipeline loop — runs report_generator every 60s
cd /home/administrator/solpulse-dashboard
while true; do
  /home/administrator/.hermes/hermes-agent/venv/bin/python3 report_generator.py >> pipeline.log 2>&1
  sleep 15
done
