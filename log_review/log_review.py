# Python script for creating a CSV with summary information from the .tlf and .hpc.tlf TUFLOW log files that can be copied and pasted into the modeling log worksheet
# Last updated on 01/20/2021 by SJP

# Step 1 - copy this script for use into your review folder
# Step 2 - set the ..\\log\\runID folder, the ..\\review\\runID folder, and the modeler's initials
# Step 3 - check the CSV file created in the review folder and copy to the modeling log worksheet

import os
import pandas as pd
import numpy as np
import datetime as dt
import shutil
import matplotlib.pyplot as plt

import logging
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# VARIABLES - MAKE CHANGES HERE (set folders and modeler)
# example: 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_1_EDDPD\\runs\\Log\\125'
log_folder = 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_2_DPDMRY\\runs\\Log\\182'
# example: 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_3_MRYFR\\review\\125'
review_folder = 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_2_DPDMRY\\review'
# person who ran model
modeler = 'SJP'

# DO NOT CHANGE ANYTHING BELOW (unless you know what you are doing)

# return volumes as strings (convert ' to 000)
def vol_str(num):
    num_str = '%i' % num
    mag = 0
    while len(num_str) > 6:
        mag += 1
        num_str = '%i' % int(num / (1000 ** mag))
    return num_str + ("\'" * mag)

# return volumes as an integer
def raw_vol(num):
    return int(vol_str(num).replace("\'", ''))

# read .tlf and record information to csv
def log_info(tlf_filename, *args, **kwargs):
    get_strs = {'BC Database == ': lambda line, get_str: line.split('\\')[-1].replace('\n', ''),
                'Simulation Started: ': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'End Time (h): ': lambda line, get_str: line.split(get_str)[1].split('.')[0].replace(' ', ''),
                'CPU Time: ': lambda line, get_str: line.split('[')[1].replace(' h]', '').replace('\n', ''),
                'Clock Time: ': lambda line, get_str: line.split('[')[1].replace(' h]', '').replace('\n', ''),
                'Input File: ': lambda line, get_str: line.split('\\')[-1].replace('\n', ''),
                '.tef': lambda line, get_str: line.split('\\')[-1].split('...')[0],
                '   Geometry Control File == ': lambda line, get_str: line.split('\\')[-1].replace('\n', ''),
                '   BC Control File == ': lambda line, get_str: line.split('\\')[-1].replace('\n', ''),
                'BC Event Source == __event__ | ': lambda line, get_str: line.split(get_str)[-1].replace('\n', ''),
                'tgc>> Read Grid IWL == ': lambda line, get_str: line.split('\\')[-1].replace('\n', ''),
                'HPC HCN Repeated Timesteps: ': lambda line, get_str: line.split(get_str)[1].split('  !')[0],
                'HPC NaN Repeated Timesteps: ': lambda line, get_str: line.split(get_str)[1].split('  !')[0],
                'HPC NaN WARNING 2550: ': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'WARNINGs prior to simulation: ': lambda line, get_str: line.split(get_str)[1].split('  [')[0].replace(' ', ''),
                'WARNINGs during simulation: ': lambda line, get_str: line.split(get_str)[1].split('  [')[0].replace(' ', ''),
                'CHECKs prior to simulation: ': lambda line, get_str: line.split(get_str)[1].split('  [')[0].replace(' ', ''),
                'CHECKs during simulation: ': lambda line, get_str: line.split(get_str)[1].split('  [')[0].replace(' ', ''),
                'Volume Error (ft3):     ': lambda line, get_str: line.split(get_str)[1].split(' of Volume')[0].replace(' or', ','),
                'Final Cumulative ME:': lambda line, get_str: line.split(get_str)[1].replace(' ', '').replace('\n', '')
                }
    mat_file_get_strs = ['Read GRID CnM ==', 'Fixed Manning\'s n = ']
    mat_type = None
    mat_file = []
    out_dict = {get_str.split(':')[0]: '' for get_str in get_strs.keys()}
    with open(tlf_filename) as f:
        lines = f.readlines()
        for line in lines:
            for get_str in get_strs.keys():
                if get_str in line:
                        data = get_strs[get_str](line, get_str)
                        out_dict[get_str.split(':')[0]] = [data]
                        logging.info(f'Got {get_str} = {data}')
            # special handling for GIS Mat (global or distributed Manning's n)
            for get_str in mat_file_get_strs:
                if get_str in line:
                    mat_type = get_str
                    mat_file.append(line.split(get_str)[1].replace('\n', ''))

    log_df = pd.DataFrame.from_dict(out_dict)
    # add column for modeler (set manually by modeler variable at top of this script)
    log_df.insert(loc=2, column='modeler', value=[modeler])
    # parse datetime to desired format
    log_df['Simulation Started'] = [dt.datetime.strptime(log_df['Simulation Started'][0], '%Y-%b-%d %H:%M').strftime('%m/%d/%Y')]
    # add column for Manning's n file
    log_df.insert(loc=12, column=mat_type, value=', '.join(mat_file))

    log_path = tlf_filename.replace('.tlf', '_log_review.csv')
    log_df.to_csv(log_path, index=False)
    logging.info('\nsaved log review table: %s\n' % log_path)


# read hpc.tlf and .tlf to a dataframe
def trending_check(hpctlf_filename, *args, **kwargs):
    # number of values to check back for trending
    check_length = 500
    # slope threshold for linear regression line
    slope_thr_nwet = 0.01

    # get start row
    start_row = 0
    skip_rows = []
    with open(hpctlf_filename) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if 'iStep' in line:
                if start_row == 0:
                    start_row = i
                else:
                    skip_rows.append(i)
            if start_row != 0:
                if 'Memory released' in line:
                    skip_rows.append(i)
                if line.startswith('Repeating step'):
                    skip_rows.append(i)

    vol_convert = lambda x: int(x.replace("\'", '000'))

    def time_convert(x):
        h, m, s = x.split(':')
        return int(h) + float(m)/60 + float(s)/3600

    # parse hpc.tlf csv to dataframe
    df = pd.read_csv(hpctlf_filename, header=start_row, skiprows=skip_rows, delim_whitespace=True,
                     converters={'vol': vol_convert, 'time': time_convert})
    df.drop(['iStep', 'maxNu', 'maxNc', 'maxNd', 'dt'], axis=1, inplace=True)
    cols = df.columns[1:]

    # initialize convergence times dict ('DNC' = does not converge)
    convergence_time = {col: ['DNC'] for col in cols}

    # iterate over columns and plot/save to .png
    for col in cols:
        plt.clf()
        x = df.time
        plt.xlabel('Time (hrs)', fontsize=12)
        y = df[col]
        plt.plot(x, y)
        plt.title(col)

        if col.startswith('nWet'):
            plt.ylabel('Number of Wetted Cells', fontsize=12)
        else:
            plt.ylabel('Volume (cu.ft.)', fontsize=12)

        plt.savefig(hpctlf_filename.replace('.hpc.tlf', '_' + col + '.png'), bbox_inches='tight')

    # iterate over nWet and volume columns
    for col in cols:
        logging.info('checking %s...' % col)
        if col.startswith('nWet'):
            slope_thr = slope_thr_nwet
            # iterate through nWet values
            for i in range(check_length, len(df.time)):
                # check slope of linear regression line
                t = df.time[i - check_length: i]
                vals = df[col][i - check_length: i]
                slope, yint = np.polyfit(t, vals, deg=1)
                # check if slope of linear regression is within slope threshold
                if abs(slope) <= slope_thr:
                    convergence_time[col] = [df.time[i]]
                    break
        if col.startswith('vol'):
            for i in range(check_length, len(df.time)):
                # check if current value is equal to previous value
                previous_vals = df[col][i - check_length: i]
                current_val = df[col][i]
                if np.all([abs(raw_vol(current_val) - raw_vol(val)) <= 1 for val in previous_vals]):
                    convergence_time[col] = [df.time[i]]
                    break
            logging.info(f'range of last {check_length} volume values: [{vol_str(min(previous_vals))}, {vol_str(max(previous_vals))}]')

    # get final volume (numeric)
    final_vol = df.vol.iloc[-1]

    # save dataframe of convergence time for all observation points/linespt
    conv_df = pd.DataFrame.from_dict(convergence_time)
    # add final volume column (formatted to string with ''s)
    conv_df['final vol'] = [f'({vol_str(final_vol)})']
    conv_path = hpctlf_filename.replace('.hpc.tlf', '_hpc_summary.csv')
    conv_df.to_csv(conv_path, index=False)
    logging.info('\nsaved convergence time table: %s\n' % conv_path)

    try:
        logging.info('\nnumber of wetted cells convergence at t = %.2f' % conv_df['nWet'][0])
    except TypeError:
        logging.info('\nnumber of wetted cells DO NOT CONVERGE!')

    try:
        logging.info('volume convergence at t = %.2f' % conv_df['vol'][0])
    except TypeError:
        logging.info('volume DOES NOT CONVERGE!')

    logging.info('final volume = %s' % vol_str(final_vol))

    logging.info(
                '\nnWet convergence = previous %i values met the slope threshold value of %.4f' % (
        check_length, slope_thr_nwet))
    logging.info(
                '\nvolume convergence = previous %i values stay constant' % (
        check_length))

if __name__ == "__main__":
    for dir, subdirs, files in os.walk(log_folder):
        for log_file in files:
            if log_file.endswith('.tlf'):
                run_id = log_file.split('_')[2]
                run_id_folder = os.path.join(review_folder, run_id)
                discharge = log_file.replace('.hpc.tlf', '').replace('.tlf', '')
                discharge_folder = os.path.join(run_id_folder, discharge)

                # create new folder for run ID and subfolder for discharge, if doesn't exist
                if not os.path.exists(discharge_folder):
                    logging.info('Creating discharge folder for {0}'.format(discharge))
                    os.makedirs(discharge_folder)

                source_path = os.path.join(dir, log_file)  # path of log file in results log folder
                log_filename = os.path.join(discharge_folder, log_file)  # log filename

                # copy log file to review/runID/discharge folder
                shutil.copy(source_path, discharge_folder)
                logging.info(
                    'log files have been copied from the results folder to discharge folder for {0}'.format(discharge))

                # for hpc.tlf file
                if log_file.endswith('.hpc.tlf'):
                    # run trending check and determine final discharge
                    logging.info('Running convergence check function for {0}'.format(discharge_folder))
                    trending_check(hpctlf_filename=log_filename)
                # for regular .tlf file
                else:
                    logging.info('Running log info function for {0}'.format(discharge_folder))
                    log_info(tlf_filename=log_filename)
