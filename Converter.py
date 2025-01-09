"""
Writer: 
Tillmann Stralka 2021.Jan. 18th
Owner: 
HLP University of Leipzig
About:
Python version 2.7
Finding tiffs and gwys in given data folder, extracting time of measurement, assembling 
them in gwy file with multible dataframe container 
"""

import gwyutils
import gwy
import os, time
import sys
import numpy as np
import pandas as pd  
import shutil 



#src_path = os.path.abspath(os.path.join(os.getcwd(), 'src'))
#sys.path.append(src_path)

#print("src_path:", src_path)  # Zum Testen, um sicherzustellen, dass der Pfad korrekt ist

# Importiere utils_afm, das jetzt im src-Ordner liegt
#from utils_afm import *

# Add the src directory to the system path
#src_path = os.path.abspath(os.path.join('src'))

#print(src_path)

# Path to the neighboring 'data' folder in the local repository
data_path = os.path.abspath(os.path.join(os.getcwd(), 'data'))




###############################################################################
        #   Declare empty lines    #
###############################################################################
#Create an empty line in which all data is stored before it gets saved to another file 
#statistics_current and so are empty lines where the statistic values will be saved, and the lists will be made to csv datas 
statistics_current = []
statistics_topo = []
statistics_error = []
statistics_current_gb = []
statistics_current_grain = []
dataframes_current = []
dataframes_topo = []
dataframes_error = []
datalines_current = []
datalines_topo = []
datalines_distance = []
#For convolution declare drift at the beginning, zeros     
array_old = 0
array_old2 = 0
offset_by_drift = (0,0)
offset_by_drift2 = (0,0)
#For Line extraction
line_x_start = 46
line_y_start = 47
line_x_end = 58
line_y_end = 34 
line_res = 1000
peak_x_position = 0 #only for the beginning set 0, then it will be overwritten 



##################################################################################################
########################## Functions for Loading and Saving ######################################
##################################################################################################

def sortandlist(path):
    # Get list of files in the directory
    names = os.listdir(path)
    
    # Filter files by type
    files_topo = [k for k in names if "Topography" in k]
    files_amp = [k for k in names if "Amplitude" in k]
    files_phase = [k for k in names if "Phase" in k]  
    files_error = [k for k in names if "Error" in k]
    files_current = [k for k in names if "Current" in k]
    
    # Sort files by name, so the program goes through them chronologically
    files_topo = sorted(files_topo)
    files_amp = sorted(files_amp)
    files_phase = sorted(files_phase) 
    files_error = sorted(files_error)       
    files_current = sorted(files_current)
    
    # All files are listed here as an overview before the process starts
    print( "Folgende Current Dateien werden bearbeitet:" )
    print(files_current)
    print( "Folgende Topography Dateien werden bearbeitet:") 
    print(files_topo)
    print( "Folgende Amplituden Dateien werden bearbeitet:" )
    print(files_amp)
    print "Folgende Phasen Dateien werden bearbeitet:" 
    print(files_phase)
    print "Folgende Error Dateien werden bearbeitet:" 
    print(files_error)
    # Get Number of Elements in List for overall Histogram Plot 
    N = len(files_topo)
    print "Number of treated elements:"
    print(N)
    return N, files_topo, files_current, files_amp, files_phase, files_error

def make_folders(path):
    # Add a new directory for .gwy files
    try:
        os.makedirs(path + "gwy")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "gwy")
        os.makedirs(path + "gwy")        
    else:
        print ("Successfully made new folder")  
    path_gwy = path + "gwy"
    return path_gwy  # Return only the gwy path for now

def get_time(list_of_filenames):
    """
    Extract timestamps from a list of filenames and return sorted list.
    
    Args:
        list_of_filenames (list): List of filenames containing timestamps
        
    Returns:
        list: List of extracted timestamps (first 9 chars only)
        
    Example:
        >>> get_time(['scan_001_20230401.dat', 'scan_002_20230402.dat'])
        ['20230401', '20230402']
    """
    # Sort filenames by timestamp
    sorted(list_of_filenames, key=extract_time)
    list_TIME = []
    
    for filename in list_of_filenames:
        ending = extract_time(filename)
        if ending:
            # Take first 9 chars of timestamp
            timestamp = ending[0:9]
            list_TIME.append(timestamp)
    
    return list_TIME

def extract_time(string):
    """
    Extract timestamp from a filename string that contains timestamp pattern.
    
    Args:
        string (str): Filename containing timestamp (e.g. 'scan_2.5V_20230401_001234.dat')
        
    Returns:
        str: Extracted timestamp string, or None if no timestamp found
        
    Example:
        >>> extract_time('scan_2.5V_20230401_001234.dat') 
        '20230401_001234'
    """
    for element in string.split("_"):
        # Look for elements starting with '00' and containing '.' 
        # This pattern matches typical timestamp formats
        if "00" in element and "." in element:
            return str(element)
    return None

def assemble(n, topo, error, current, amp, phase, time_list, path_new):
    """
    Assemble multiple scan types into combined .gwy files.
    
    Args:
        n (int): Number of scans
        topo (list): Topography scan files
        error (list): Error scan files  
        current (list): Current scan files
        amp (list): Amplitude scan files
        phase (list): Phase scan files
        time_list (list): Timestamps for each scan
        path_new (str): Output directory path
    """
    # Sort files by timestamp
    sorted(topo, key=extract_time)
    sorted(error, key=extract_time)
    sorted(current, key=extract_time)
    sorted(amp, key=extract_time)
    sorted(phase, key=extract_time)

    for i in range(len(topo)):
        print('Iteration run: i=')
        print(i)
        
        # Load topography data
        TOPO = topo[i]
        ids_topo, actcon_topo = load_data(path, TOPO)
        df_topo, name_topo = select_dataframe(actcon_topo, ids_topo[0])
        
        # Get output filename from timestamp
        name = time_list[i]
        print(name)
        
        # Add error data if available
        if len(error) == 0:
            print('The Error list is empty')
        else:
            ERROR = error[i]
            ids_error, actcon_error = load_data(path, ERROR)
            df_error, name_error = select_dataframe(actcon_error, ids_error[0])
            id_error = gwy.gwy_app_data_browser_add_data_field(df_error, actcon_topo, 1)
            actcon_topo['/' + str(id_error) +'/data/title'] = 'Error'
            remove(actcon_error)
       
        # Add current data if available
        if len(current) == 0:
            print('The current list is empty')
        else:
            CURRENT = current[i]
            ids_current, actcon_current = load_data(path, CURRENT)
            df_current, name_current = select_dataframe(actcon_current, ids_current[0])
            id_current = gwy.gwy_app_data_browser_add_data_field(df_current, actcon_topo, 2)
            actcon_topo['/' + str(id_current) +'/data/title'] = 'Current'
            remove(actcon_current)
                        
        # Add amplitude data if available
        if len(amp) == 0:
            print('The Amplitude list is empty')
        else:
            AMP = amp[i]
            ids_amp, actcon_amp = load_data(path, AMP)
            df_amp, name_amp = select_dataframe(actcon_amp, ids_amp[0])
            id_amp = gwy.gwy_app_data_browser_add_data_field(df_amp, actcon_topo, 3)
            actcon_topo['/' + str(id_amp) +'/data/title'] = 'Amplitude'
            remove(actcon_amp)    
            
        # Add phase data if available
        if len(phase) == 0:
            print('The Phase list is empty')
        else:
            PHASE = phase[i]
            ids_phase, actcon_phase = load_data(path, PHASE)
            df_phase, name_phase = select_dataframe(actcon_phase, ids_phase[0])
            id_phase = gwy.gwy_app_data_browser_add_data_field(df_phase, actcon_topo, 4)
            actcon_topo['/' + str(id_phase) +'/data/title'] = 'Phase'
            remove(actcon_phase) 
            
        # Save combined file
        actcon_topo = data_save(actcon_topo, name, path_newData, path)
        remove(actcon_topo)

    return

def load_data(path, name):
    print("Es wird gerade folgende Datei bearbeitet:")
    print(name)
    
    
    os.chdir(path)
    #Load data from path
    actcon = gwy.gwy_file_load(name, gwy.RUN_NONINTERACTIVE)
    #Load container into browser
    gwy.gwy_app_data_browser_add(actcon)
    #Ids is identifikation code or key of the active container 
    ids = gwy.gwy_app_data_browser_get_data_ids(actcon)
    print "With the following ids:"
    print ids
    return ids, actcon


def select_dataframe(actcon, key):
    #Select df with key id 0 since the tiff only has one 
    df = actcon[gwy.gwy_app_get_data_key_for_id(key)] 
    df_name = actcon["/" + str(key) +"/data/title"]
    print "The name of the datafield as represented in the gwy container:"
    print df_name
    title = df_name
    actcon["/" + str(key) +"/data/title"] = title
    #Select datafield so that the fit functions (gwy_process_func_run) are not confused
    gwy.gwy_app_data_browser_select_data_field(actcon, key)
    return df, df_name

def remove(actcon):
    #Remove file from browser to prevent program crashes due to overload
    gwy.gwy_app_data_browser_remove(actcon)	

def data_save(actcon, fname, path_saving, path_working):
    #Save files as a new .gwy file with a _fitted ending
    os.chdir(path_saving)
    #gwy.gwy_file_save(actcon, fname)
    
    gwy.gwy_file_save(actcon, fname + ".gwy")
    os.chdir(path_working)
    return actcon

###############################################################################
    ### The Program itself 
###############################################################################
  
path = data_path
N, fnames_topo, fnames_current, fnames_amp, fnames_phase, fnames_error = sortandlist(path) 

path_newData = make_folders(path)

time_list =  get_time(fnames_topo)

assemble(N, fnames_topo, fnames_error, fnames_current, fnames_amp, fnames_phase, time_list, path_newData) 

###############################################################################
    ### End of Program 
###############################################################################

print('End of Program')
