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
        if [[ "${JOBS[i]}" == "$job" ]]; then
            echo "[~] Ignoring the job <${JOBS[i]}> because it's already in the crontab."
            isInserted=true
            break
        fi
    done < tempcron
    if [ $isInserted = false ]; then
        echo "${JOBS[i]}" >> tempcron

        #Enter job into the crontab
        crontab tempcron >/dev/null 2>&1
        
        #Interpret exit code
        RESULT=$?
        if [ $RESULT -eq 0 ]; then
            echo "[O] Successfully entered <${JOBS[i]}>!"
        else
            echo "[X] Crontab failed with error code $RESULT while trying to enter <${JOBS[i]}>."

            #Reset tempcron
            crontab -l > tempcron
        fi
    fi
    i=$((i + 1))
done



#cleanup
rm tempcron
exit $RESULT
