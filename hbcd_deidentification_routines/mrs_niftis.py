from spec2nii.spec2nii import main
import sys
import os


def deid_mrs_nifti(input_file_name, output_file_name):
    '''Routine to remove sensitive metadata from mrs niftis
    
    Parameters
    ----------
    input_file_name: str
        Path to a mrs nifti file (probably following something
        like /bids/sub-<label>/ses-<label>/mrs/*.nii.gz)
    output_file_name: str
        The path to the mrs nifti file that will be created
        by this function.
    
    Returns
    -------
    The path to the ouput file that has been created.
    
    
    '''
    
    if os.path.exists(input_file_name) == False:
        raise NameError('Error: No MRS Nifti with the following name exists {}'.format(input_file_name))
        
    

    fields_to_remove = ['InstitutionName', 'InstitutionAddress', 'PatientSex', 'PatientWeight']
    for temp_field in fields_to_remove:
        if os.path.exists(output_file_name) == False:
            sys.argv = ["spec2nii", "anon", input_file_name, '-f', output_file_name.replace('.nii.gz', ''), '-r', temp_field]
        else:
            sys.argv = ["spec2nii", "anon", output_file_name, '-f', output_file_name.replace('.nii.gz', ''), '-r', temp_field]
        main()
        
    if os.path.exists(output_file_name) == False:
        raise ValueError('Error: the current script was supposed to create a new nifti with the following path, but that didnt happen {}'.format(output_file_name))
        
    return output_file_name