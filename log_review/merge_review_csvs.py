import os
import pandas as pd

import logging
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

review_folder = 'Z:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_1_EDDPD\\review\\133'

# initializing csv file lists
hpc_files = []
review_files = []
PO_conv_files = []

# initializing dataframes
hpc_sum = pd.DataFrame()
log_review = pd.DataFrame()
PO_conv = pd.DataFrame()
review_summary = pd.DataFrame()

# defining the run id from folder being review
run_id = review_folder.split('\\')[-1]

for dir, subdirs, files in os.walk(review_folder):
    for review_file in files:
        review_filename = os.path.join(dir, review_file)
        # add hpc summary csv files to hpc_files list
        logging.info(f'{run_id}: Adding hpc_summary.csv files to list...')
        if review_file.endswith('hpc_summary.csv'):
            hpc_files.append(review_filename)
        # add log review csv files to review_files list
        logging.info(f'{run_id}: Adding log_review.csv files to list...')
        if review_file.endswith('log_review.csv'):
            review_files.append(review_filename)
        # PO convergence csv files to PO_files list
        logging.info(f'{run_id}: Adding PO_convergence.csv files to list...')
        if review_file.endswith('PO_convergence_times.csv'):
            PO_conv_files.append(review_filename)

for f in hpc_files:
    # read csv files into data frame from hpc_file list
    logging.info(f'{run_id}: Reading hpc_summary.csv files to data frame...')
    df = pd.read_csv(f)
    hpc_sum = hpc_sum.append(df, ignore_index=True)

for f in review_files:
    # read csv files into data frame from review_files list
    logging.info(f'{run_id}: Reading log_review.csv files to data frame...')
    df = pd.read_csv(f)
    log_review = log_review.append(df, ignore_index=True)

for f in PO_conv_files:
    # read csv files into data from from PO_conv_files list
    logging.info(f'{run_id}: Reading PO_convergence_times.csv files to data frame...')
    df = pd.read_csv(f)
    PO_conv = PO_conv.append(df, ignore_index=True)
    # subset to columns we care about
    PO_conv = PO_conv[['V conv time', 'Q conv time', 'Comments']]

logging.info(f'{run_id}: Concatenating data frames into review summary data frame...')
review_summary = pd.concat([log_review, hpc_sum, PO_conv], axis=1, join='inner', sort=True)
review_sum_path = os.path.join(review_folder, f'{run_id}_review_summary.csv')
logging.info(f'{run_id}: Writing review summary to {review_sum_path}...')
review_summary.to_csv(review_sum_path, index=False)



