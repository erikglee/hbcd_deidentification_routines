from nibabel import cifti2
import nibabel as nib
import os, glob

def update_cifti_metadata(original_img_name, output_file_name, dccid, guid):
    
    parent_directory = os.path.dirname(output_file_name)
    if parent_directory and not os.path.exists(parent_directory):
        os.makedirs(parent_directory)
    
    original_img = nib.load(original_img_name)
    header = original_img.header
    matrix = header.matrix
    content_for_inspection = []

    # Print general metadata
    matrix_metadata = getattr(matrix, 'metadata', None)
    if matrix_metadata:
        if True:
            print("General Metadata:")
        for temp_key in matrix_metadata.keys():
            matrix_metadata[temp_key] = matrix_metadata[temp_key].replace(dccid, guid)
            if True:
                print(f"{temp_key}: {matrix_metadata[temp_key]}")
            content_for_inspection.append(temp_key)
            content_for_inspection.append(matrix_metadata[temp_key])

    
    
    original_data = original_img.get_fdata()
    new_img = cifti2.Cifti2Image(original_data, header = original_img.header)
    nib.save(new_img, output_file_name) 
    
    return