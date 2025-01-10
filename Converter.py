"""
Script Information
-------------------
Writer:      Tillmann Stralka
Date:        2021-01-18
Owner:       HLP University of Leipzig
Python Ver.: 2.7

Description:
This script finds TIFF and GWY files in a specified data folder, extracts the 
measurement times, and assembles them into a GWY file with multiple data frame 
containers.
"""

# Standard Library Imports
import os
import sys

# Third-Party Library Imports
import numpy as np
import pandas as pd
import gwy

# Local Imports
# Import utils_afm from the src directory
src_path = os.path.abspath(os.path.join('src'))
print("src path:", src_path)

# Add the src directory to the system path
sys.path.append(src_path)
from utils_afm import *

# Define the path to the 'data' folder in the local repository
data_path = os.path.abspath(os.path.join(os.getcwd(), 'data'))
# Define the general working directory / path 
path = os.path.abspath(os.path.join(os.getcwd()))

###############################################################################
# Main Program
###############################################################################

# Sort and list the files in the directory; returns file names grouped by type
N, fnames_topo, fnames_current, fnames_amp, fnames_phase, fnames_error = sortandlist(data_path)

# Create folders for storing the processed data
path_newData = make_folders(path)   

# Extract timestamps from the topology files
time_list = get_time(fnames_topo)

# Assemble the data using the listed file names and timestamps
assemble(
    N, 
    fnames_topo, 
    fnames_error, 
    fnames_current, 
    fnames_amp, 
    fnames_phase, 
    time_list, 
    data_path,
    path_newData
)

###############################################################################
# End of Program
###############################################################################

print('Program execution completed.')

