"""
These functions make sure that only studies with correctly formatted files are
saved and allowed to be analysed.
"""

import os
import numpy as np
import pandas as pd
import shutil
from frontend import app
from werkzeug.utils import secure_filename
from frontend.view_functions import get_user_folder

# -----------------------------------------------------------------------------
# CHECK FILES MAIN FUNCTION
# -----------------------------------------------------------------------------

def check_files(user_data_folder, files_dict, form):
    """
    Checks if the uploaded files have the correct format
    """
    # -------------------------------------------------------------------------
    # SET UP OF VARIABLES
    format_errors = dict()
    # this will show a top panel on the form, informing the user
    format_errors['misformatted'] = ''
    study_folder = secure_filename(form.study_name.data)

    # -------------------------------------------------------------------------
    # CHECKING DATASETS
    # -------------------------------------------------------------------------
    datasets = ['dataset1']
    samples = []
    probes = []
    #TODO: Add checks for remaining file formats
    #PDB files are currently not checked
    #datasets.append('dataset2')
    #datasets.append('dataset3')

    for dataset in datasets:
        # check if we can open the file
        try:
            dataset_path = os.path.join(user_data_folder, files_dict[dataset])
            df, sep = open_file(dataset_path)
        except:
            format_errors[dataset] = ['Could not open this file.']
            clear_up_study(study_folder)
            return False, format_errors

        # check if we have enough numeric columns in all data files
        df_numeric = df.select_dtypes(include=[np.number])

        # save row and col names of datasets
        samples.append(df_numeric.index)
        probes.append(df_numeric.columns)
        min_numeric = app.config['MINIMUM_FEATURES']
        if df_numeric.shape[1] < min_numeric:
            format_errors[dataset] = ['Datasets must have at least %s numeric'
                                      ' columns.' % min_numeric]
            clear_up_study(study_folder)
            return False, format_errors

        # check dataset dimensions
        if (df.shape[0] > app.config['MAX_SAMPLES'] or
            df.shape[1] > app.config['MAX_FEATURES']):
            format_errors[dataset] = ['The dimensions of this dataset exceed '
                                      'the supported maximum.']
            clear_up_study(study_folder)
            return False, format_errors

    # everything went fine, every file is checked
    return True, format_errors

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def clear_up_study(study_folder):
    """
    Deletes the uploaded files if they are mis-formatted.
    """
    user_folder = get_user_folder()
    folder_to_delete = os.path.join(user_folder, study_folder)
    if os.path.exists(folder_to_delete):
        shutil.rmtree(folder_to_delete)

def open_file(file_path, **kwargs):
    """
    Opens files based on their file extension in pandas
    """
    filename, extension = os.path.splitext(file_path)
    #There is additional check in the code
    if extension == '.txt' or  extension == '.dat':
        sep = '\s+'
    file = pd.read_csv(file_path, sep=sep, index_col=None, header=None, **kwargs)
    return file, sep
