#!/usr/bin/env python
import os
import argparse    


def my_parser():

    parser = argparse.ArgumentParser(description="Replace text in .set files.")
    parser.add_argument("input_path_to_eventlogs_file", help="Path to the eventlogs.txt file with identifiable meta-data.")
    parser.add_argument("output_path_to_eventlogs_file", help="Path to the eventlogs.txt file that you want to be created with de-identified meta-data.")
    parser.add_argument("GUID", help="The de-identified identifier to replace the DCCID and PSCID.")
    return parser.parse_args()

def deidentify_sourcedata_eventlogs_file(input_file_path, output_file_path, guid):
    '''De-identifies eeg sourcedata eventlogs.txt files
    
    input_file_path : str
        Path to file to be de-identified. Assumes BIDS formatting
        of file-name (sub-<label>_ses-<label>_task-<label>_acq-eeg_eventlogs.txt)
    output_file_path : str
        Path of file to be created. If subject label is 12345 and session
        label is 01, then the sequence 12345_01 will be replaced with
        the new sequence <guid>_01
    guid : str
        The guid that will be replacing the subject label in the output
        file.
    
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
        
    sub_partial = subject_component.split('-')[1]
    ses_partial = session_component.split('-')[1]
    old_text = '{}_{}'.format(sub_partial, ses_partial)
    new_text = '{}_{}'.format(guid, ses_partial)
    
    with open(input_file_path, 'r', encoding='UTF-16') as f:
        oldlines = f.readlines()
    with open(output_file_path, 'w', encoding='UTF-16') as f:
        for templine in oldlines:
            f.write(templine.replace(old_text, new_text))
            
    return


def main():
    args = my_parser()
    deidentify_sourcedata_eventlogs_file(args.input_path_to_eventlogs_file, args.output_path_to_eventlogs_file, args.GUID)


# Call the fucntion
if __name__ == "__main__":
    main()