#!/bin/bash
# SolPulse watchdog: hourly health-check + auto-restart + git progress commit.
cd /home/administrator/solpulse-dashboard
LOG=watchdog.log

say(){ echo "[$(date -u +%FT%TZ)] $*" >> $LOG; }

while true; do
  # 1) HTTP server on 8081
  if ! curl -s -o /dev/null http://127.0.0.1:8081/dashboard.html; then
    say "http.server down — restarting"
    nohup python3 -m http.server 8081 --bind 127.0.0.1 --directory /home/administrator/solpulse-dashboard >/dev/null 2>&1 &
  fi

  # 2) pipeline loop daemon
  if ! pgrep -f "pipeline_loop.sh" >/dev/null; then
    say "pipeline_loop down — restarting"
    nohup bash pipeline_loop.sh >/dev/null 2>&1 &
  fi

  # 3) public tunnel (localhost.run rotates URL on restart)
  code=$(curl -s -o /dev/null -w "%{http_code}" -m 15 https://d5f3f47e8e06ee.lhr.life/dashboard.html)
  if [ "$code" != "200" ]; then
    say "tunnel unhealthy ($code) — restarting ssh tunnel"
    pkill -f "ssh.*localhost.run" 2>/dev/null
    sleep 2
    nohup ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:127.0.0.1:8081 nokey@localhost.run >/tmp/tunnel.log 2>&1 &
    sleep 8
    newurl=$(grep -o 'https://[a-z0-9]*\.lhr\.life' /tmp/tunnel.log | head -1)
    say "new tunnel url: ${newurl:-UNKNOWN} (update dashboards/links)"
  fi

  # 4) hourly git progress commit
  if ! git diff --quiet HEAD 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "chore: automated progress checkpoint [watchdog]" >/dev/null 2>&1 && \
      git push origin main >/dev/null 2>&1 && say "committed+pushed" || say "commit/push issue"
  fi

  sleep 3600
done
