#!/bin/sh
# Boot script for the Sprog host.
# Lives at /home/ec2-user/run_sprog.sh on the machine and is run by cron at
# boot (@reboot). Transcribed from the Jan 2017 original on the host — same
# steps in the same order. The only intentional change is the Python line,
# which uses the venv (/home/ec2-user/sprog-venv/bin/python) instead of the
# old `python35`. The live file on the machine is untouched; this copy exists
# so the host can be rebuilt from the repo alone.
export HOME=/home/ec2-user
export PATH=/usr/local/bin:/usr/bin:/bin
cd /home/ec2-user/sprog || exit 1
# Rotate logs: log -> log-1 -> log-2 -> log-3
[ -f log-2 ] && mv log-2 log-3
[ -f log-1 ] && mv log-1 log-2
[ -f log ] && mv log log-1
git pull origin master
/home/ec2-user/sprog-venv/bin/python main.py &> log
sudo shutdown -h +10
