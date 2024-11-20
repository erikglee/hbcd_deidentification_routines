#!/usr/bin/env python
import h5py
import numpy as np
import argparse

def my_parser():
    parser = argparse.ArgumentParser(description="Replace text in .mat files.")
    parser.add_argument("input_path", help="Path to the .mat file with identifiable meta-data.")
    parser.add_argument("output_path", help="Path to the .matt file that you want to be created with de-identified meta-data.")
    parser.add_argument("DCCID", help="A type of HBCD identifier to be eliminated from .mat file.")
    parser.add_argument("PSCID", help="A type of HBCD identifier to be eliminated from .mat file.")
    parser.add_argument("GUID", help="The de-identified identifier to replace the DCCID and PSCID.")
    return parser.parse_args()

# Define the replace function
def replace_in_strings(text, old, new):
    """Replace all occurrences of `old` with `new` in a given string."""
    return text.replace(old, new)


def replace_text_in_mat_file(input_path,DCCID, PSCID, GUID):
   # Open the input .mat file
    with h5py.File(input_path, 'r') as f_in:
        # List all items in the file
        #print("Keys in file:", list(f.keys()))
  
        # Access specific elements within the structure
        struct_array = f_in['MRSCont']
        output_folder = struct_array['outputFolder'][()]
        loaded_job = struct_array['loadedJob'][()]
  

        # Decode the data and remove null characters
        decoded_output_folder = output_folder.tobytes().decode('utf-8').replace('\x00', '')
        decoded_loaded_job = loaded_job.tobytes().decode('utf-8').replace('\x00', '')
        


        # Replace values in the decoded data
        modified_data = {
            'outputFolder': replace_in_strings(decoded_output_folder, 'sub-{}'.format(DCCID), 'sub-{}'.format(GUID)),
            'loadedJob': replace_in_strings(decoded_loaded_job, 'sub-{}'.format(DCCID), 'sub-{}'.format(GUID))
                    }

        # Further replacement on the entire dictionary
        modified_data['outputFolder'] = replace_in_strings(modified_data['outputFolder'], PSCID, GUID)
        modified_data['loadedJob'] = replace_in_strings(modified_data['loadedJob'], PSCID, GUID)


        # Save the modified data to a new .mat file in v7.3 format
    with h5py.File(input_path, 'a') as f_out:
        if 'MRSCont' in f_out:

            del f_out['MRSCont/outputFolder']
            del f_out['MRSCont/loadedJob']
        # Create a group to match the structure in the original file
        MRSCont_group = f_out.create_group('MRSCont')
    
        # Add modified data back into the file structure
        MRSCont_group.create_dataset('outputFolder', data=np.bytes_(modified_data['outputFolder']))
        MRSCont_group.create_dataset('loadedJob', data=np.bytes_(modified_data['loadedJob']))

    print(f"Data saved in v7.3 .mat format at {input_path}")
   

  



# Call the fucntion

if __name__ == "__main__":
    args = my_parser()
    replace_text_in_mat_file(args.input_path,args.DCCID, args.PSCID, args.GUID)



    
