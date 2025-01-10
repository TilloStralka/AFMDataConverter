"""
AFM Data Processing Utility Functions

This module contains functions for processing and analyzing AFM (Atomic Force Microscopy) data.
Functions are organized into the following categories:

-------------------------------------

1. Loading and Saving
   - Functions for file I/O operations, path handling, and data import/export.
   - Includes:
     - `load_data(path, name)`: Loads a `.gwy` file and adds it to the GWY data browser.
     - `data_save(actcon, fname, path_saving, path_working)`:
       Saves the active container as a `.gwy` file and manages directory navigation.

2. Data Processing
   - Functions for selecting and manipulating data fields from active containers.
   - Includes:
     - `select_dataframe(actcon, key)`: Selects a data field based on its key ID 
       and prepares it for further processing.
     - `remove(actcon)`: Removes an active container from the GWY data browser 
       to prevent overload or crashes.

3. Helper Functions
   - Utility functions for timestamp extraction and processing.
   - Includes:
     - `get_time(list_of_filenames)`: Extracts timestamps from a list of filenames.
     - `extract_time(string)`: Extracts timestamp patterns from a single filename string.

4. Pipeline Functions
   - Functions for sorting, organizing, and assembling data from multiple scan types.
   - Includes:
     - `sortandlist(path)`: Sorts and organizes files by type (e.g., Topography, Amplitude, etc.)
       and provides an overview of the files to be processed.
     - `make_folders(path)`: Creates directories for output storage, specifically for `.gwy` files.
     - `assemble(n, topo, error, current, amp, phase, time_list, path_new)`:
       Combines data from various scan types into `.gwy` files for further analysis.

-------------------------------------       

Each function is documented with its specific purpose and parameters.
"""

# Standard Library Imports
import os
import sys
import shutil

# Third-Party Library Imports
import numpy as np
import pandas as pd
import gwy

# Path to the data 
path = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))

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
    print( "Folgende Phasen Dateien werden bearbeitet:"  )
    print(files_phase)
    print( "Folgende Error Dateien werden bearbeitet:"  )
    print(files_error)
    # Get Number of Elements in List for overall Histogram Plot 
    N = len(files_topo)
    print( "Number of treated elements:" )
    print(N)
    return N, files_topo, files_current, files_amp, files_phase, files_error

def make_folders(path):
    # Add a new directory for .gwy files
    try:
        os.makedirs(path + "/gwy")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "/gwy")
        os.makedirs(path + "/gwy")        
    else:
        print ("Successfully made new folder")  
    path_gwy = path + "/gwy"
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

def assemble(n, topo, error, current, amp, phase, time_list, path, path_newData):
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
    """
    Load a .gwy file from the specified directory and add it to the GWY data browser.

    Args:
        path (str): The directory containing the .gwy file.
        name (str): The name of the .gwy file to be loaded.

    Returns:
        tuple: A tuple containing:
            - ids (list): Identification codes (keys) of the data fields in the active container.
            - actcon (object): The active container object holding the loaded data.
    """
    print("Processing the following file:")
    print(name)

    # Change to the specified directory
    os.chdir(path)

    # Load the .gwy file non-interactively
    actcon = gwy.gwy_file_load(name, gwy.RUN_NONINTERACTIVE)

    # Add the loaded container to the data browser
    gwy.gwy_app_data_browser_add(actcon)

    # Retrieve identification codes (keys) of the active container's data fields
    ids = gwy.gwy_app_data_browser_get_data_ids(actcon)
    print("Loaded with the following IDs:")
    print(ids)
    
    return ids, actcon


def select_dataframe(actcon, key):
    """
    Select a data field from the active container based on its key ID.

    Args:
        actcon (object): The active container object holding the data.
        key (int): The key ID of the data field to be selected.

    Returns:
        tuple: A tuple containing:
            - df (object): The data field corresponding to the key ID.
            - df_name (str): The name of the data field as stored in the container.
    """
    # Retrieve the data field using the key ID
    df = actcon[gwy.gwy_app_get_data_key_for_id(key)]
    
    # Get the name of the data field
    df_name = actcon["/" + str(key) + "/data/title"]
    print("The name of the data field in the GWY container:")
    print(df_name)

    # Update the title for clarity
    title = df_name
    actcon["/" + str(key) + "/data/title"] = title

    # Select the data field in the browser to ensure compatibility with processing functions
    gwy.gwy_app_data_browser_select_data_field(actcon, key)
    
    return df, df_name


def remove(actcon):
    """
    Remove the active container from the GWY data browser to prevent overload or crashes.

    Args:
        actcon (object): The active container object to be removed.
    """
    gwy.gwy_app_data_browser_remove(actcon)

    return

def data_save(actcon, fname, path_saving, path_working):
    """
    Save the active container to a new .gwy file with a specified filename.

    Args:
        actcon (object): The active container object holding the data to be saved.
        fname (str): The desired filename for the saved file (without extension).
        path_saving (str): The directory where the file should be saved.
        path_working (str): The directory to return to after saving.

    Returns:
        object: The active container object after saving.
    """
    # Change to the saving directory
    os.chdir(path_saving)

    # Save the active container as a .gwy file with a "_fitted" suffix
    gwy.gwy_file_save(actcon, fname + ".gwy")

    # Change back to the working directory
    os.chdir(path_working)
    
    return actcon