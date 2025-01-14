#!/usr/bin/env python
import os
import scipy
import numpy as np
import argparse    


#These routines were originally written by Monalisa Bilas with edits from Erik Lee (9/3/2024)

#The replace_text_in_set_file is function that can be used on it's own, or this whole script
#can be run from the command line using the arguments denoted in my_parser

def my_parser():

    parser = argparse.ArgumentParser(description="Replace text in .set files.")
    parser.add_argument("input_path_to_set_file", help="Path to the .set file with identifiable meta-data.")
    parser.add_argument("output_path_to_set_file", help="Path to the .set file that you want to be created with de-identified meta-data.")
    parser.add_argument("DCCID", help="A type of HBCD identifier to be eliminated from .set file.")
    parser.add_argument("PSCID", help="A type of HBCD identifier to be eliminated from .set file.")
    parser.add_argument("GUID", help="The de-identified identifier to replace the DCCID and PSCID.")
    return parser.parse_args()


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
                print('   Pattern found: {}'.format(old_pattern))
                data[key] = new_string

    # If the data is a list or tuple, recursively apply the function to each element
    elif isinstance(data, list):
        for i in range(len(data)):
            change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
            if change_needed:
                print('   Pattern found: {}'.format(old_pattern))
                data[i] = new_string
    elif isinstance(data, tuple):
        change_needed, new_string = replace_in_strings(list(data), old_pattern, new_pattern)
        if change_needed:
            print('   Pattern found: {}'.format(old_pattern))
            data = tuple(new_string)

    # If the data is a NumPy array, handle both structured and unstructured arrays
    elif isinstance(data, np.ndarray):
        if data.dtype.str.startswith('<U'):
            if int(data.dtype.str.split('U')[1]) < minimum_pattern_length:
                change_ever_needed = False
                for i in range(len(data)):
                    change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
                    if change_needed:
                        print('   Pattern found: {}'.format(old_pattern))
                        data[i] = new_string
                        change_ever_needed = True
                return change_ever_needed, data
            else:
                #print('Temporarily changing numpy array with shape {} and dtype {} to <U300'.format(data.shape, data.dtype.str))
                new_ndarray = np.empty(data.shape, dtype='<U300')
                change_ever_needed = False
                maximum_observed_length = 0
                for i in range(len(data)):
                    change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
                    if len(new_string) > maximum_observed_length:
                        maximum_observed_length = len(new_string)
                    if change_needed:
                        print('   Pattern found: {}'.format(old_pattern))
                        new_ndarray[i] = new_string
                        change_ever_needed = True
                if change_ever_needed:
                    new_ndarray = new_ndarray.astype('<U{}'.format(maximum_observed_length))
                    data = new_ndarray
                    #print('   final type: {}'.format(data.dtype.str))
                return change_ever_needed, data
        else:
            change_ever_needed = False
            for i in range(len(data)):
                change_needed, new_string = replace_in_strings(data[i], old_pattern, new_pattern)
                if change_needed:
                    print('   Pattern found: {}'.format(old_pattern))
                    data[i] = new_string
                    change_ever_needed = True
            return change_ever_needed, data

    # If the data is a numpy.void object (e.g., a record in a structured array), handle its fields
    elif isinstance(data, np.void):
        change_ever_needed = False
        for field_name in data.dtype.names:
            change_needed, new_string = replace_in_strings(data[field_name], old_pattern, new_pattern)
            if change_needed:
                print('   Pattern found: {}'.format(old_pattern))
                data[field_name] = new_string
                change_ever_needed = True
        return change_ever_needed, data

    # If the data is a string, replace the old pattern with the new one
    elif isinstance(data, str):
        #print('Potentially String.')
        new_string = data.replace(old_pattern, new_pattern)
        if new_string != data:
            print('   Pattern found: {}'.format(old_pattern))
            return True, new_string
        else:
            return False, data

    # If the data is a bytes object, replace the old pattern with the new one
    elif isinstance(data, bytes):
        #print('Potentially changing bytes string.')
        new_string = data.replace(old_pattern.encode(), new_pattern.encode())
        if new_string != data:
            print('   Pattern found: {}'.format(old_pattern))
            return True, new_string
        else:
            return False, data

    # If the data is a NumPy string, replace the old pattern with the new one
    elif isinstance(data, np.str_):
        #print('Potentially changing numpy string.')
        new_string = data.replace(old_pattern, new_pattern)
        if new_string != data:
            print('   Pattern found: {}'.format(old_pattern))
            return True, new_string
        else:
            return False, data

    # If the data is a NumPy bytes string, replace the old pattern with the new one
    elif isinstance(data, np.bytes_):
        #print('Potentially changing encoded bytes string.')
        new_string = np.bytes_(data.replace(old_pattern.encode(), new_pattern.encode()))
        if new_string != data:
            print('   Pattern found: {}'.format(old_pattern))
            return True, new_string
        else:
            return False, data

    # For any other data types, return the data as is
    #print(type(data))
    return False, data



def replace_text_in_set_file(input_path_to_set_file, output_path_to_set_file, DCCID, PSCID, GUID):
    """Load a .set file, replace text, and save the modified file."""
    set_data = scipy.io.loadmat(input_path_to_set_file)
    
    allowed_event_cell_entries = ['PDEV', 'STND', 'REEG', 'objects', 'DVNT',
                                  'Checkerboard', 'Baseline', 'inverted', 'uprightINV',
                                  'uprightOBJ', 'Background', 'V03', 'V04', 'V06']
    
    if 'EEG' in set_data.keys():
        #This means we have an EEG file (not an ECG file)
        #with specific fields we will attempt to de-identify
        try:
            partial_copy = set_data['EEG'][0][0][39][0][0][5][0][0][0][0][0][1]
            if int(partial_copy.dtype.str.split('U')[1]) < 10:
                partial_copy = partial_copy.astype('<U10')
            partial_copy[0] = 'Anonymized'
            set_data['EEG'][0][0][39][0][0][5][0][0][0][0][0][1] = partial_copy
        except:
            print('   unable to adjust expected Patient ID field for: {}'.format(input_path_to_set_file))
            
            
        try:
            for i in range(set_data['EEG'][0][0][25][0].shape[0]):
                temp_type = set_data['EEG'][0][0][25][0][i][7][0]
                if temp_type == 'CELL':
                    partial_copy = set_data['EEG'][0][0][25][0][i][3]
                    if int(partial_copy.dtype.str.split('U')[1]) < 10:
                        partial_copy = partial_copy.astype('<U10')
                    if partial_copy[0] not in allowed_event_cell_entries:
                        partial_copy[0] = 'Anonymized'
                        set_data['EEG'][0][0][25][0][i][3] = partial_copy
        except:
            print('   unable to adjust CELL entries of event struct for: {}'.format(input_path_to_set_file))
            
    elif 'acq-eeg' in input_path_to_set_file:
        raise NameError('Error: acq-eeg file found without EEG field at top level of data structure. This file should be skipped until routines to handle this are developed.')

        
        
    #Also run generic de-id for both EEG/ECG files
    _, set_data = replace_in_strings(set_data, 'sub-{}'.format(DCCID), 'sub-{}'.format(GUID))
    _, set_data = replace_in_strings(set_data, '{}_{}'.format(PSCID, DCCID), GUID)
    _, set_data = replace_in_strings(set_data, PSCID, GUID)

    parent_folder = os.path.dirname(output_path_to_set_file)
    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)
    scipy.io.savemat(output_path_to_set_file, set_data, appendmat = False)
    print(f"Processed {input_path_to_set_file} and saved to {output_path_to_set_file}")
    
    return

def main():
    args = my_parser()
    replace_text_in_set_file(args.directory_path, args.DCCID, args.PSCID, args.GUID)


# Call the fucntion
if __name__ == "__main__":
    main()