#!/bin/bash

# Config
PLOT=/home/pi/.local/bin/stressberry-plot
# TEMP_MIN=0
# TEMP_MAX=40
# Passive Cooling
TEMP_MIN=30
TEMP_MAX=90
D_TEMP_MIN=0
D_TEMP_MAX=70
TEMP_MIN=30
TEMP_MAX=90
FREQ_MIN=400
FREQ_MAX=2200
DPI=300
LINE_WIDTH=0.2
FILE_FORMAT=.png

for f in *.out
  do
     echo "$f"
     MPLBACKEND=Agg $PLOT "$f" -f -d $DPI -t $TEMP_MIN $TEMP_MAX -l $FREQ_MIN $FREQ_MAX -o "${f%.out}$FILE_FORMAT" --hide-legend --not-transparent --line-width $LINE_WIDTH
     MPLBACKEND=Agg $PLOT "$f" -f -d $DPI -t $D_TEMP_MIN $D_TEMP_MAX -l $FREQ_MIN $FREQ_MAX -o "${f%.out}-delta$FILE_FORMAT" --hide-legend --not-transparent --line-width $LINE_WIDTH --delta-t
done

