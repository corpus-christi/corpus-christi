# Dev Ops

## Hosting

- We host with [Linode](https://www.linode.com/).
- We use [Travis CI](https://travis-ci.org/)
  for continuous integration and delivery.

## System Set-Up

In order to enable automated operations (like pruning events), run:
```
./set-up-cron-jobs.sh
```
This script inserts a job into your crontab that will archive events that ended more than 30 days before running. This job will run (by default) every day at 3:30 AM, but you can run it at a different time by changing the crontab's attributes before running the script.
