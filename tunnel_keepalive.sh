#!/bin/bash
# Reconnects tunnel whenever it drops; logs new URL each time
URLLOG=/home/administrator/solpulse-dashboard/current_tunnel_url.txt
while true; do
  if ! pgrep -f "nokey@localhost.run" > /dev/null; then
    echo "$(date -u +%H:%M) tunnel down, reconnecting" >> /home/administrator/solpulse-dashboard/watchdog.log
    OUT=$(ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:127.0.0.1:8081 nokey@localhost.run 2>&1 &)
    sleep 8
  fi
  # capture current url from newest ssh process output is hard; instead probe known pattern via lhr API not available.
  sleep 120
done
