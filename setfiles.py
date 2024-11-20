#!/usr/bin/env python
import os
import shutil
import scipy
import numpy as np
import argparse    




#These routines were originally written by Monalisa Bilas with edits from Erik Lee (9/3/2024)

#The replace_text_in_set_file is function that can be used on it's own, or this whole script
#can be run from the command line using the arguments denoted in my_parser



def replace_in_strings(data, old_pattern, new_pattern):
    """
    Recursively traverses a data structure to find strings and replace a pattern with a new one.
    
    Parameters:
    - data: The data structure to traverse (can be dict, list, tuple, np.array, or any object).
    - old_pattern: The pattern to search for in strings.
    - new_pattern: The pattern to replace with in strings.
    
    Returns:
    - The modified data structure with the pattern replaced in strings.
    """
    # If the data is a dictionary, recursively apply the function to each value
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_in_strings(value, old_pattern, new_pattern)

    # If the data is a list or tuple, recursively apply the function to each element
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = replace_in_strings(data[i], old_pattern, new_pattern)
    elif isinstance(data, tuple):
        data = tuple(replace_in_strings(list(data), old_pattern, new_pattern))

    # If the data is a NumPy array, handle both structured and unstructured arrays
    elif isinstance(data, np.ndarray):
        if data.dtype.str.startswith('<U'):
            new_ndarray = np.empty(data.shape, dtype='U100')
            for i in range(len(data)):
                new_ndarray[i] = replace_in_strings(data[i], old_pattern, new_pattern)
            return new_ndarray
        else:
            for i in range(len(data)):
                data[i] = replace_in_strings(data[i], old_pattern, new_pattern)

    # If the data is a numpy.void object (e.g., a record in a structured array), handle its fields
    elif isinstance(data, np.void):
        for field_name in data.dtype.names:
            data[field_name] = replace_in_strings(data[field_name], old_pattern, new_pattern)

    # If the data is a string, replace the old pattern with the new one
    elif isinstance(data, str):
        return data.replace(old_pattern, new_pattern)

    # If the data is a bytes object, replace the old pattern with the new one
    elif isinstance(data, bytes):
        return data.replace(old_pattern.encode(), new_pattern.encode())

    # If the data is a NumPy string, replace the old pattern with the new one
    elif isinstance(data, np.str_):
        return np.str_(data.replace(old_pattern, new_pattern), dtype='U100')

    # If the data is a NumPy bytes string, replace the old pattern with the new one
    elif isinstance(data, np.bytes_):
        return np.bytes_(data.replace(old_pattern.encode(), new_pattern.encode()))

    # For any other data types, return the data as is
    #print(type(data))
    return data



def replace_text_in_set_file(input_path_to_set_file, output_path_to_set_file, DCCID, PSCID, GUID):
    """Load a .set file, replace text, and save the modified file."""
    set_data = scipy.io.loadmat(input_path_to_set_file)
    set_data = replace_in_strings(set_data, 'sub-{}'.format(DCCID), 'sub-{}'.format(GUID))
    set_data = replace_in_strings(set_data, '{}_{}'.format(PSCID, DCCID), GUID)
    set_data = replace_in_strings(set_data, PSCID, GUID)

    parent_folder = os.path.dirname(output_path_to_set_file)
    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)
    scipy.io.savemat(output_path_to_set_file, set_data, appendmat = False)
    
    
  
def my_parser():
    parser = argparse.ArgumentParser(description="Replace text in .set files.")
    parser.add_argument("input_path_to_set_file", help="Path to the .set file with identifiable meta-data.")
    parser.add_argument("output_path_to_set_file", help="Path to the .set file that you want to be created with de-identified meta-data.")
    parser.add_argument("DCCID", help="A type of HBCD identifier to be eliminated from .set file.")
    parser.add_argument("PSCID", help="A type of HBCD identifier to be eliminated from .set file.")
    parser.add_argument("GUID", help="The de-identified identifier to replace the DCCID and PSCID.")
    return parser.parse_args()



    
# Call the fucntion
if __name__ == "__main__":
    args = my_parser()
    

    
    directory_path = '/home/faird/shared/projects/HBCD_MIDB_IG/example_data/eeg_test_for_monalisa/bids_before_deidentification/sub-349836/ses-V03/eeg/'
    output_path ='/home/faird/shared/projects/HBCD_MIDB_IG/example_data/eeg_test_for_monalisa/output_after_deidentification/'
   
    # Split the path by "/" and filter out empty strings
    path_parts = [part for part in directory_path.split("/") if part]

    # Get the last three elements
    last_three = path_parts[-3:]

    # Join the last three elements to form the new directory path
    new_dir = os.path.join(output_path, *last_three)

    # Create the new directory recursively
    os.makedirs(new_dir, exist_ok=True)
    
    
    # List of files ending with .sat
    set_files = [f for f in os.listdir(directory_path) if f.endswith('.set')]
    fdt_files = [f for f in os.listdir(directory_path) if f.endswith('.fdt')]

    for file in set_files:
        input_path_to_set_file = os.path.join(directory_path, file)
        output_path_to_set_file = os.path.join(directory_path, file)
        # Call the function and pass the variables parsed by argparse
        replace_text_in_set_file(input_path_to_set_file, output_path_to_set_file, args.DCCID, args.PSCID, args.GUID)
        shutil.copy(output_path_to_set_file,new_dir)
        print(f"Processed {input_path_to_set_file} and saved to {new_dir}")
        
    for file in fdt_files:
        input_path_to_set_file = os.path.join(directory_path, file)
        output_path_to_set_file = os.path.join(directory_path, file)
        shutil.copy(output_path_to_set_file,new_dir)
        print(f"Processed {input_path_to_set_file} and saved to {new_dir}")
        