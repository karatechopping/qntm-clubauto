#!/bin/bash
# ~/run_cron_every_minute.sh
#removed:  . ~/.bashrc
cd /home/qntmfitlife/qntmapi/clubauto
/home/qntmfitlife/qntmapi/clubauto/myenv/bin/python3.11 main.py --run_csv=True --run_ghl=True --run_email=False --attach_csv=False --sample_size=-1 --run_log=False --days_back=1