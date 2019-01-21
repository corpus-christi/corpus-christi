crontab -l > tempcron
crontab -l  > refcron

#Enter all new jobs to be created below the current entries:
echo "30 3 * * * \$(cd $(pwd); . ./set-up-bash.sh; flask maintain prune-events) >/dev/null 2>&1" >> tempcron

if [[ $(tail -n 1 ./tempcron) == $(tail -n 1 ./refcron) ]]; then
    echo "Jobs already created, exiting."
    exit 1
fi
crontab tempcron
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "Successfully entered the crontab!"
else
    echo "Crontab failed with error code $RESULT."
fi
rm tempcron
rm refcron
exit $RESULT
