#!/bin/sh

# Setup the crontab
echo "$CRON_SCHEDULE /run-backup.py" | crontab -

# Start the cron daemon
exec crond -f
