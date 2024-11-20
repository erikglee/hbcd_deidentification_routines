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