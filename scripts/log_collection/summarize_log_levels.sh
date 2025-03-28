#!/bin/bash

# Summarizes occurrence counts of log levels in device, log consumer, and
# database pod logs. Pod logs in LOGS_DIR are analyzed and the summary is
# created in LOG_LEVEL_SUMMARY_FILE.

### Directory/file and log level control parameters ###
SCRIPT_DIR=$(dirname "$0")
LOGS_DIR="$SCRIPT_DIR/../../logs"

LOG_LEVEL_SUMMARY_FILE="$LOGS_DIR/log_level_summary.txt"
DEVICE_LOG_LEVELS=("CRITICAL" "ERROR" "WARNING" "INFO" "DEBUG")
DATABASE_LOG_LEVELS=("Error" "Warning" "Note")

function add_log_level_heading() {
    TABLE_HEADING_STR=$1
    local -n LOG_LEVELS=$2
    for LOG_LEVEL in ${LOG_LEVELS[@]}; do
        TABLE_HEADING_STR+=" $LOG_LEVEL"
    done
    echo $TABLE_HEADING_STR
}

##### Write out table count of log level occurrences for device server logs #####
echo "DEVICE SERVER LOGS:" > $LOG_LEVEL_SUMMARY_FILE

### Device server summarization parameters ###
DEVICE_SERVER_LOG_FILE_PREFIX="ds-"

### Construct and write table ###
DS_TABLE_OUT="DeviceServerLogFile"
DS_TABLE_OUT=$(add_log_level_heading $DS_TABLE_OUT "DEVICE_LOG_LEVELS")
DS_TABLE_OUT+=$'\n'

DEVICE_SERVER_LOG_FILES=$(ls $LOGS_DIR | grep "^$DEVICE_SERVER_LOG_FILE_PREFIX")
for LOG_FILE in ${DEVICE_SERVER_LOG_FILES[@]}; do
    DS_TABLE_OUT+=$LOG_FILE
    LOG_FILE_PATH="$LOGS_DIR/$LOG_FILE"
    for LOG_LEVEL in ${DEVICE_LOG_LEVELS[@]}; do
        OCCURRENCE_COUNT=$(grep "|$LOG_LEVEL|" $LOG_FILE_PATH | wc -l)
        DS_TABLE_OUT+=" $OCCURRENCE_COUNT"
    done
    DS_TABLE_OUT+=$'\n'
done

echo $"$DS_TABLE_OUT" | column -t >> $LOG_LEVEL_SUMMARY_FILE
echo "" >> $LOG_LEVEL_SUMMARY_FILE

##### Write out table count of log level occurrences for each device in logconsumer #####
echo "CONSUMER LOGS:" >> $LOG_LEVEL_SUMMARY_FILE

### Log consumer summarization parameters ###
LOG_CONSUMER_LOG_FILE="ds-talondxlogconsumer-001-0.log"
DEVICE_LOG_LINE_PREFIX="tango-device:"
DEVICE_LOG_LINE_DELIMITER="|"
DEVICE_LOG_LINE_NAME_INDEX=7
DEVICE_LOG_LINE_LEVEL_INDEX=3

### Construct and write table ###
TEMP_CONSUMER_FILE_PATH="$LOGS_DIR/temp_consumer.txt"
> "$TEMP_CONSUMER_FILE_PATH"

while IFS= read -r LINE; do
    CAND_DEVICE_NAME=$(echo $LINE | cut -d $DEVICE_LOG_LINE_DELIMITER -f $DEVICE_LOG_LINE_NAME_INDEX)
    if echo $CAND_DEVICE_NAME | grep -q $DEVICE_LOG_LINE_PREFIX; then
        DEVICE_NAME=$(echo $CAND_DEVICE_NAME | sed -e s/^$DEVICE_LOG_LINE_PREFIX//)
        DEVICE_LOG_LEVEL=$(echo "$LINE" | cut -d $DEVICE_LOG_LINE_DELIMITER -f $DEVICE_LOG_LINE_LEVEL_INDEX)
        echo $DEVICE_NAME $DEVICE_LOG_LEVEL >> "$TEMP_CONSUMER_FILE_PATH"
    fi
done < "$LOGS_DIR/$LOG_CONSUMER_LOG_FILE"

sort -o $TEMP_CONSUMER_FILE_PATH $TEMP_CONSUMER_FILE_PATH

LC_TABLE_OUT="LogConsumerDevice"
LC_TABLE_OUT=$(add_log_level_heading $LC_TABLE_OUT "DEVICE_LOG_LEVELS")
LC_TABLE_OUT+=$'\n'

CURR_CHUNK=""
if [ -s $TEMP_CONSUMER_FILE_PATH ]; then
    LAST_DEVICE_NAME=$(head -n 1 $TEMP_CONSUMER_FILE_PATH | cut -d " " -f 1)
    while IFS= read -r LINE; do
        CURRENT_DEVICE_NAME=$(echo $LINE | cut -d " " -f 1)
        if [ $CURRENT_DEVICE_NAME != $LAST_DEVICE_NAME ]; then
            LC_TABLE_OUT+=$CURRENT_DEVICE_NAME
            for LOG_LEVEL in ${DEVICE_LOG_LEVELS[@]}; do
                OCCURRENCE_COUNT=$(echo $CURR_CHUNK | grep $LOG_LEVEL | wc -l)
                LC_TABLE_OUT+=" $OCCURRENCE_COUNT"
            done
            LC_TABLE_OUT+=$'\n'
            CURR_CHUNK=""
            LAST_DEVICE_NAME=$CURRENT_DEVICE_NAME
        else
            CURR_CHUNK+=$LINE
            CURR_CHUNK+=$'\n'
        fi
    done < $TEMP_CONSUMER_FILE_PATH
    LC_TABLE_OUT+=$'\n'
fi

echo $"$LC_TABLE_OUT" | column -t >> $LOG_LEVEL_SUMMARY_FILE
echo "" >> $LOG_LEVEL_SUMMARY_FILE

##### Write out table count of log level occurrences for each database log #####
echo "DATABASE LOGS:" >> $LOG_LEVEL_SUMMARY_FILE

### Database summarization parameters ###
DATABASE_LOG_FILE_PREFIX="database"

DB_TABLE_OUT="DatabaseLog"
DB_TABLE_OUT=$(add_log_level_heading $DB_TABLE_OUT "DATABASE_LOG_LEVELS")
DB_TABLE_OUT+=$'\n'

### Construct and write table ###
DATABASE_LOG_FILES=$(ls $LOGS_DIR | grep "^$DATABASE_LOG_FILE_PREFIX")
for LOG_FILE in ${DATABASE_LOG_FILES[@]}; do
    DB_TABLE_OUT+=$LOG_FILE
    LOG_FILE_PATH="$LOGS_DIR/$LOG_FILE"
    for LOG_LEVEL in ${DATABASE_LOG_LEVELS[@]}; do
        OCCURRENCE_COUNT=$(grep "$LOG_LEVEL" $LOG_FILE_PATH | wc -l)
        DB_TABLE_OUT+=" $OCCURRENCE_COUNT"
    done
    DB_TABLE_OUT+=$'\n'
done

echo $"$DB_TABLE_OUT" $'\n' | column -t >> $LOG_LEVEL_SUMMARY_FILE
