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



def replace_text_in_set_file(input_path_to_set_file, output_path_to_set_file, DCCID, PSCID, GUID):
    """Load a .set file, replace text, and save the modified file."""
    set_data = scipy.io.loadmat(input_path_to_set_file)
    #print(set_data)
    # print(set_data.keys())

    try:
        if "ecg_eeg" in input_path_to_set_file.split('/')[-1]:
            #print(set_data['setname'][0])
            set_data['setname'][0] = set_data['setname'][0].replace(PSCID,GUID)
            print(set_data['setname'][0])
         
        elif "eeg_eeg" in input_path_to_set_file.split('/')[-1]:
            temp = set_data['EEG'][0][0][0]
            temp[0] = GUID
            temp = temp[0].astype(str)
            temp_1 = set_data['EEG'][0][0][1]
            temp_1[0] = GUID
            temp_1 = temp_1[0].astype(str)
            set_data['EEG'][0][0][0] = temp.replace(DCCID, GUID).rstrip()
            set_data['EEG'][0][0][1] = temp_1.replace(DCCID, GUID).rstrip()
            print(set_data['EEG'][0][0][0])
            print(set_data['EEG'][0][0][1])
       
    except KeyError:
        print("Tags  'EEG' and 'setname' not found in the dictionary. Please check the key name.")

    parent_folder = os.path.dirname(output_path_to_set_file)
    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)
    scipy.io.savemat(output_path_to_set_file, set_data)
    print(f"Processed {input_path_to_set_file} and saved to {output_path_to_set_file}")

# Call the fucntion
if __name__ == "__main__":

    args = my_parser()
    replace_text_in_set_file(args.directory_path, args.DCCID, args.PSCID, args.GUID)