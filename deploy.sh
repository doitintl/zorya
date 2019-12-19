#!/usr/bin/env bash

if [[ $# -eq 0 ]] ; then
 echo Missing project id argument
 exit
fi

PROJECTID=`gcloud projects list | grep -iw "$1" | awk '{print $1}'`

if [ -z "$PROJECTID" ]; then
 echo Project $1 Not Found!
 exit
fi

echo Project ID $PROJECTID
gcloud config set project $PROJECTID

rm -rf ./build
cd client && yarn install && yarn build && cd ..
##Build the task queue


if gcloud tasks queues list|grep zorya-tasks >/dev/null 2>&1; then
  echo "Task Queue all ready exists"
else
  gcloud tasks queues create zorya-tasks
fi
loc=`gcloud tasks queues describe zorya-tasks|grep name`
LOCATION="$(echo $loc | cut -d'/' -f4)"
echo

file_location='util/location.py'
if [ -f "$file_location" ]; then
  rm $file_location
  fi
cat > $file_location <<EOF
def get_location():
    return "${LOCATION}"
EOF

gcloud app deploy -q app.yaml cron.yaml
