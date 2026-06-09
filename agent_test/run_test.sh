#!/bin/bash
##############################################################################
#
# Script filename       : run_test.sh
#
# Config filename       : na
#
# Date created          : 24 Oct 2025
#
# Last Modification     : na
#
# Created by            : R.Graceffa
#
# Modified by           : R.Graceffa
#
# Description           : run LLMs test
#
#
##############################################################################

###########################################################
# Global parameters
###########################################################

SCRIPT_NAME=${0##*/}
MYDATE=$(date '+%Y-%m-%d')
BASE_FOLDER="/home/azureuser/agent_test"
TEST_FOLDER="$BASE_FOLDER/test"
LOG_FOLDER="$BASE_FOLDER/log"
LOG_FILE="$LOG_FOLDER/${SCRIPT_NAME%.sh}_$MYDATE.log"
REFERENCE_TEST_FILE="README"
RESULT_TEST_FILE="RESULT_$MYDATE"
STARTPVTGPT="cd /home/azureuser/private-gpt; source venv/bin/activate; PGPT_PROFILES=ollama make run"
GPT_LOG_FILE="pvtgpt_$MYDATE.log"
GPT_SLEEP_TIME=40
RUNCOMMAND="cd /home/azureuser/private-gpt; source venv/bin/activate; python3 $BASE_FOLDER/test_agent_file.py "

#####################
# Useful Functions 
#####################

function log {
        datetime=`date`
        echo "$*"
        echo "$datetime [$SCRIPT_NAME] -- PID " "$$" " -- " "$*" >> $LOG_FILE
} # end of function log

function get_pid {
        # parameters:
        #  - process_name       the process name to get the pid of
        PROCESS=$1
        TMP=`ps -eaf | grep "$PROCESS" |grep -v grep| awk '{print $2}'`
        echo $TMP
} # end of function get_pid



###########################################################
# Main Cycle
###########################################################

MYTASKTYPE=`ls $TEST_FOLDER`

log "--------- Start Operations ------------------"
for MYTASK in $MYTASKTYPE
do
	#echo $MYTASK
	MYTASKID=`ls -d $TEST_FOLDER/$MYTASK/* | sort -n`
	for MYTESTID in $MYTASKID
	do
		#echo "|-> $MYTESTID"
		MYFINALFOLDER="$MYTESTID"
		log "--------- Start Task ------------------"
		log "Start Processing $MYTESTID..."
		#Check if REFERENCE_TEST_FILE exists
		if [ -s "$MYFINALFOLDER/$REFERENCE_TEST_FILE" ]; then
		  log "$REFERENCE_TEST_FILE exists and is not empty."
		  TASKNAME=`grep TASKNAME $MYFINALFOLDER/$REFERENCE_TEST_FILE | cut -f2 -d=`
		  TASKPRE_EXECUTION=`grep TASKPRE_EXECUTION $MYFINALFOLDER/$REFERENCE_TEST_FILE | cut -f2 -d=`
		  TASKCOMMAND=`grep TASKCOMMAND $MYFINALFOLDER/$REFERENCE_TEST_FILE | cut -f2 -d=`
		  TASKVERIFY=`grep TASKVERIFY $MYFINALFOLDER/$REFERENCE_TEST_FILE | cut -f2 -d=`
		  TASKPOST_EXECUTION=`grep TASKPOST_EXECUTION $MYFINALFOLDER/$REFERENCE_TEST_FILE | cut -f2 -d=`
		  echo "TASKNAME: "$TASKNAME
		  echo "TASKPRE_EXECUTION: "$TASKPRE_EXECUTION
		  echo "TASKCOMMAND: "$TASKCOMMAND
		  echo "TASKVERIFY: "$TASKVERIFY
		  echo "TASKPOST_EXECUTION: "$TASKPOST_EXECUTION
		  #Run the local private gpt
		  nohup bash -c "$STARTPVTGPT" > $MYFINALFOLDER/$GPT_LOG_FILE 2>&1 &
		  GPT_PID=$!
                  log "PrivateGPT started in background with PID: $GPT_PID"
		  sleep $GPT_SLEEP_TIME
		  #Create a loop to submit max 5 times the command to private gpt
		  #for i in {1..5}; do
		  #	log "Attempt $i..." 
			#Inject the command to the private gpt
			bash -c "$RUNCOMMAND $MYFINALFOLDER/$REFERENCE_TEST_FILE" > $MYFINALFOLDER/$RESULT_TEST_FILE
			# MYRESULT=`grep SUCCESS $MYFINALFOLDER/$RESULT_TEST_FILE`
		    # if [ -n "$MYRESULT" ]; then
			  # log "Attempt $i ended with success..." 
			  # break
			# else
			  # log "Attempt $i had no success. Retrying for 5 times max." 
			# fi  
		  #done
		  #Shutdown the private gpt
		  kill $GPT_PID 
		  log "PrivateGPT stopped from background with PID: $GPT_PID"
		else
		  log "$REFERENCE_TEST_FILE does not exist or empty."
		fi
		log "End Processing $MYTESTID..."	
	done

done


log "--------- End Operations ------------------"
exit 0

