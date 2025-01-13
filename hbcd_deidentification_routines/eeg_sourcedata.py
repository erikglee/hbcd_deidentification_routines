#!/usr/bin/env python
import os
import argparse
import pandas as pd    


def my_parser():

    parser = argparse.ArgumentParser(description="Replace text in .set files.")
    parser.add_argument("input_path_to_eventlogs_file", help="Path to the eventlogs.txt file with identifiable meta-data.")
    parser.add_argument("output_path_to_eventlogs_file", help="Path to the eventlogs.txt file that you want to be created with de-identified meta-data.")
    parser.add_argument("GUID", help="The de-identified identifier to replace the DCCID and PSCID.")
    return parser.parse_args()

def deidentify_sourcedata_eventlogs_file(input_file_path, output_file_path):
    '''De-identifies eeg sourcedata eventlogs.txt files
    
    input_file_path : str
        Path to file to be de-identified. Assumes BIDS formatting
        of file-name (sub-<label>_ses-<label>_task-<label>_acq-eeg_eventlogs.txt)
    output_file_path : str
        Path to de-identified file.
    
    '''
    
    if input_file_path.endswith('eventlogs.txt') == False:
        raise ValueError('Error: expected file with naming structure like sub-<label>_ses-<label>_task-<label>_acq-eeg_eventlogs.txt')

    partial_file_name = input_file_path.split('/')[-1]
    partial_file_name_split = partial_file_name.split('_')
    if len(partial_file_name_split) < 2:
        raise ValueError('Error: expected file with naming structure like sub-<label>_ses-<label>_task-<label>_acq-eeg_eventlogs.txt')
    subject_component = partial_file_name.split('_')[0]
    session_component = partial_file_name.split('_')[1]
    
    if subject_component.startswith('sub-')*session_component.startswith('ses-') == False:
        raise ValueError('Error: expected file with naming structure like sub-<label>_ses-<label>_task-<label>_acq-eeg_eventlogs.txt')
        
    directory = os.path.dirname(output_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        df = pd.read_csv(input_file_path, delimiter='\t', encoding='UTF-16')
    except:
        raise ValueError('Error: Unable to load the following file. Likely because it isnt a real tsv or because it doesnt exist. File: {}'.format(input_file_path))
    fields_to_check = ['DataFile.Basename', 'DCCID', 'Subject']
    for temp_field in fields_to_check:
        df[temp_field] = 'Anonymized'
        
    df.to_csv(output_file_path, encoding='UTF-16', index=False, sep='\t')
    return


def main():
    args = my_parser()
    deidentify_sourcedata_eventlogs_file(args.input_path_to_eventlogs_file, args.output_path_to_eventlogs_file)


# Call the fucntion
if __name__ == "__main__":
    main()