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
    - A boolean indicating whether the data structure was modified.
    """

    minimum_pattern_length = len(old_pattern)

    # If the data is a dictionary, recursively apply the function to each value
    if isinstance(data, dict):
        for key, value in data.items():
            change_needed, new_string = replace_in_strings(value, old_pattern, new_pattern)
            if change_needed:
                data[key] = new_string

    # If the data is a list or tuple, recursively apply the function to each element
    elif isinstance(data, list):
        for i in range(len(data)):
            change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
            if change_needed:
                data[i] = new_string
    elif isinstance(data, tuple):
        change_needed, new_string = replace_in_strings(list(data), old_pattern, new_pattern)
        if change_needed:
            data = tuple(new_string)

    # If the data is a NumPy array, handle both structured and unstructured arrays
    elif isinstance(data, np.ndarray):
        if data.dtype.str.startswith('<U'):
            if int(data.dtype.str.split('U')[1]) < minimum_pattern_length:
                change_ever_needed = False
                for i in range(len(data)):
                    change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
                    if change_needed:
                        data[i] = new_string
                        change_ever_needed = True
                return change_ever_needed, data
            else:
                print('Temporarily changing numpy array with shape {} and dtype {} to <U300'.format(data.shape, data.dtype.str))
                new_ndarray = np.empty(data.shape, dtype='<U300')
                change_ever_needed = False
                maximum_observed_length = 0
                for i in range(len(data)):
                    change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
                    if len(new_string) > maximum_observed_length:
                        maximum_observed_length = len(new_string)
                    if change_needed:
                        new_ndarray[i] = new_string
                        change_ever_needed = True
                if change_ever_needed:
                    new_ndarray = new_ndarray.astype('<U{}'.format(maximum_observed_length))
                    data = new_ndarray
                    print('   final type: {}'.format(data.dtype.str))
                return change_ever_needed, data
        else:
            change_ever_needed = False
            for i in range(len(data)):
                change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
                if change_needed:
                    data[i] = new_string
                    change_ever_needed = True
            return change_ever_needed, data

    # If the data is a numpy.void object (e.g., a record in a structured array), handle its fields
    elif isinstance(data, np.void):
        change_ever_needed = False
        for field_name in data.dtype.names:
            change_needed, new_string = replace_in_strings(data[field_name], old_pattern, new_pattern)
            if change_needed:
                data[field_name] = new_string
                change_ever_needed = True
        return change_ever_needed, data

    # If the data is a string, replace the old pattern with the new one
    elif isinstance(data, str):
        #print('Potentially String.')
        new_string = data.replace(old_pattern, new_pattern)
        if new_string != data:
            return True, new_string
        else:
            return False, data

    # If the data is a bytes object, replace the old pattern with the new one
    elif isinstance(data, bytes):
        #print('Potentially changing bytes string.')
        new_string = data.replace(old_pattern.encode(), new_pattern.encode())
        if new_string != data:
            return True, new_string
        else:
            return False, data

    # If the data is a NumPy string, replace the old pattern with the new one
    elif isinstance(data, np.str_):
        #print('Potentially changing numpy string.')
        new_string = data.replace(old_pattern, new_pattern)
        if new_string != data:
            return True, new_string
        else:
            return False, data

    # If the data is a NumPy bytes string, replace the old pattern with the new one
    elif isinstance(data, np.bytes_):
        #print('Potentially changing encoded bytes string.')
        new_string = np.bytes_(data.replace(old_pattern.encode(), new_pattern.encode()))
        if new_string != data:
            return True, new_string
        else:
            return False, data

    # For any other data types, return the data as is
    #print(type(data))
    return False, data


def replace_text_in_set_file(input_path_to_set_file, output_path_to_set_file, DCCID, PSCID, GUID):
    
    
    # Split the path by "/" and filter out empty strings
    path_parts = [part for part in input_path_to_set_file.split("/") if part]
    # Get the last three elements
    last_three = path_parts[-3:]
    # Join the last three elements to form the new directory path
    new_dir = os.path.join(output_path_to_set_file, *last_three)
    # Create the new directory recursively
    os.makedirs(new_dir, exist_ok=True)
    
    # List of files ending with .sat
    set_files = [f for f in os.listdir(input_path_to_set_file) if f.endswith('.set')]
    fdt_files = [f for f in os.listdir(input_path_to_set_file) if f.endswith('.fdt')]
    for file in set_files:
        
        input_path = os.path.join(input_path_to_set_file, file) # is a file
        output_path_to_set_file = os.path.join(input_path_to_set_file, file) # is a file
        #print(input_path)   
        
        """Load a .set file, replace text, and save the modified file."""
        set_data = scipy.io.loadmat(input_path)
        
        set_data = replace_in_strings(set_data, 'sub-{}'.format(DCCID), 'sub-{}'.format(GUID))
        set_data = replace_in_strings(set_data, '{}_{}'.format(PSCID, DCCID), GUID)
        set_data = replace_in_strings(set_data, PSCID, GUID)
        parent_folder = os.path.dirname(output_path_to_set_file)
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)
        scipy.io.savemat(output_path_to_set_file, set_data, appendmat = False)
        #print(output_path_to_set_file)
        shutil.copy(output_path_to_set_file,new_dir)
        print(f" Processed {input_path_to_set_file}  set files and saved to {new_dir}")
    
   
        
    for file in fdt_files:
        input_path = os.path.join(input_path_to_set_file, file)
        #output_path_to_set_file = os.path.join(input_path_to_set_file, file)
        shutil.copy(input_path,new_dir)
        
        print(f"  Processed {input_path_to_set_file} fdt files  and saved to {new_dir}")
        
    
    
    
  
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
    replace_text_in_set_file(args.input_path_to_set_file, args.output_path_to_set_file, args.DCCID, args.PSCID, args.GUID)

    
    
    
        
        
       
        
         
        


