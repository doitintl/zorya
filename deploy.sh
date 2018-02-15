#!/usr/bin/env bash

PROJECTID=`gcloud projects list | grep -i $1 |  awk '{print $1}'`
if [ -z "$PROJECTID" ]; then
 echo Project $1 Not Found!
 exit
fi
echo Project ID $PROJECTID
gcloud config set project $PROJECTID



gcloud app deploy -q app.yaml cron.yaml queue.yaml
