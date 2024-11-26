import os, glob

def remove_cifti_provenance(input_file_name, output_file_name,
                              wb_command_path='/common/software/install/manual/workbench/2.0.1-rocky8/bin/wb_command'):
    
    
    if os.path.exists(wb_command_path) == False:
        raise ValueError('Error: No file found at the expected location of wb_command. This must be set correctly for the function to work.')
    
    
    parent_directory = os.path.dirname(output_file_name)
    if parent_directory and not os.path.exists(parent_directory):
        os.makedirs(parent_directory)
    
    os.system('{}  -metadata-remove-provenance  {} {}'.format(wb_command_path, input_file_name, output_file_name))
    
    return