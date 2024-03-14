#!/bin/bash

# Write out current crontab
crontab -l > mycron

# Echo new cron into cron file
# Schedule to run at 6 AM UTC daily, adjust as necessary
echo "0 22 * * * /usr/bin/python /var/app/current/src/components/reddit_components/data_extract.py >> /var/app/current/logs/data_extract.log 2>&1" >> mycron

# Install new cron file
crontab mycron
rm mycron