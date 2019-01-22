#!/bin/bash

crontab -l > tempcron

#Enter all new jobs to be created as a new entry in the array (JOBS[1], JOBS[2], etc).
JOBS[0]='30 3 * * * $(cd $(pwd); . ./set-up-bash.sh; flask maintain prune-events) >/dev/null 2>&1'
NUM_JOBS=${#JOBS[@]}

#Making sure that each job isn't already in the crontab
i=0
while [ $i -lt $NUM_JOBS ]; do
    isInserted=false
    while read job; do
        if [[ ${JOBS[i]} == $job ]]; then
            echo "Ignoring the job <${JOBS[i]}> because it's already in the crontab."
            isInserted=true
            break
        fi
    done < tempcron
    if [ $isInserted = false ]; then
        echo "${JOBS[i]}" >> tempcron
        echo "Will try to add job <${JOBS[i]}>."
    fi
    i=$((i + 1))
done

#Enter tempcron into the crontab
crontab tempcron

#Interpret exit code
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "Successfully entered the crontab!"
else
    echo "Crontab failed with error code $RESULT."
fi

#cleanup
rm tempcron
exit $RESULT
