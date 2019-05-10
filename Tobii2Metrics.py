#!/usr/bin/env python
# coding: utf-8

#   Copyright (C) 2019  Cesco Willemse
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

# # # # # # # # # # # # #
#   USED TO GENERATE A METRICS FILE FROM THE TOBII RAW .TSV OUTPUT WITH PYGAZEANALYSER FUNCTIONS.
#
#   Pygaze Analyser Copyright (C) 2014  Edwin S. Dalmaijer - https://github.com/esdalmaijer/PyGazeAnalyser
#
#   Requires the following user inputs:
#       - Path to pygaze PyGazeAnalyser
#       - Path of input tsv file
#       - Output path and filename
#       - Any parameters in the functions you'd like to adjust from the default.
# # # # # # # # # # # # #

# Firstly, PyGazeAnalyser is not on PyPi as a package and installing it from Github with pip does not seem to work.
# Of course, other ways to add it to your python environment permanently are available,
# But here I just append it to my path for this python instance. (example given, use youw own path).
import sys
sys.path.append('/Path/To/anaconda2/lib/python2.7/site-packages/PyGazeAnalyser/pygazeanalyser')

# Importing detectors from PyGazeAnalyser, plus my standard go-to's.
import pandas as pd
import detectors
import numpy as np
import os
import math

# Reading the PyGaze log file.
# The first 17 lines comprise a calibration report, line 18 contains the headers.
# FOR FUTURE:
# It would be great to also use the leading information because it automatically reports fixation thresholds, but I
# don't know how to do it with the current format.
# Also, in case of multiple calibrations during a single experiment, a more intelligent parsing method is likely to be
# required (untested).
df = pd.read_csv('/path/to/TOBII_output.tsv', sep = '\t', skiprows = range (0,17))

# Define which values to use in the PyGaze functions (corresponding to columns in the output).
x = df['GazePointX']
y = df['GazePointY']
time = df['TimeStamp']

# # # # # # # # # # # # #
# FIXATIONS
# # # # # # # # # # # # #

# Using default max dist in this example, could be updated according to aforementioned calibration report
fixations = detectors.fixation_detection(x, y, time, missing=0.0, maxdist=25, mindur=50)
Efix = fixations[1]
df_fix = pd.DataFrame(Efix, columns = ['starttime', 'endtime', 'duration', 'endx', 'endy'])
df_fix['label']='fixation' # add label

# # # # # # # # # # # # #
# SACCADES
# # # # # # # # # # # # #

# Default values except minlen - 20ms, was 5.
saccades = detectors.saccade_detection(x, y, time, missing=0.0, minlen=20, maxvel=40, maxacc=340)
Esac = saccades[1]
df_sac = pd.DataFrame(Esac, columns = ['starttime', 'endtime', 'duration', 'startx', 'starty', 'endx', 'endy'])
# FOR FUTURE: calculate amplitude with PY-thagoras. In current shape numpy throws a negative value error.
# df_sac['amplitude'] = np.sqrt((df_sac['endx']-df_sac['startx'])^2 + (df_sac['endy']-df_sac['starty'])^2)
df_sac['label']='saccade'

# # # # # # # # # # # # #
# USER MESSAGES (I.E. TRIGGERS)
# # # # # # # # # # # # #

df_triggers = df[df['Event'].notnull()] # Only when Events is not blank.
df_triggers['starttime'] = df_triggers['TimeStamp']
df_triggers['label']='message'
df_triggers = df_triggers[['starttime','Event','label']]

# # # # # # # # # # # # #
# BLINKS
# # # # # # # # # # # # #

# For tobii, missing = -1.
blinks = detectors.blink_detection(x, y, time, missing=-1, minlen=10)
Eblk = blinks[1]
df_blk = pd.DataFrame(Eblk, columns = ['starttime', 'endtime', 'duration'])
df_blk['label'] = 'blink'

# # # # # # # # # # # # #
# OUTPUT
# # # # # # # # # # # # #

df_metrics = df_triggers.append([df_fix, df_sac, df_blk],ignore_index=True, sort=False) # Append all dataframes.
df_metrics = df_metrics.sort_values(by=['starttime']) # Sort by starttime (= timestamp).
df_metrics = df_metrics.reset_index(drop=True) # Reset the index.

# Save to file (use own output path and name)
df_metrics.to_csv('/path/to/filename.csv',index=False)
