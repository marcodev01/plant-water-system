#!/usr/bin/env bash
PROJECT_PATH=/home/pi/Projects/plantWaterSystem
API_SCRIPTPATH=/home/pi/Projects/plantWaterSystem/src/api

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "ERROR: Run script as root!"
    sleep 3
    exit
fi

echo starting api server: $API_SCRIPTPATH
source $PROJECT_PATH/venv/bin/activate
cd $API_SCRIPTPATH
uvicorn api:app --host 0.0.0.0 --port 80