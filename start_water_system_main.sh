#!/usr/bin/env bash
PROJECT_PATH=~/Projects/plantWaterSystem
WATER_SYSTEM_SCRIPTPATH=~/Projects/plantWaterSystem/src/waterSystem

echo starting water system: $WATER_SYSTEM_SCRIPTPATH
source $PROJECT_PATH/venv/bin/activate
cd $WATER_SYSTEM_SCRIPTPATH
python3 water_system_runner.py
