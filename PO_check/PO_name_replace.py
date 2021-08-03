# Python script for changing incorrect naming of PO (points or lines) in the PO.csv files
# All names must start with 'Pt' or 'Ln' for the PO_convergence script to be used
# Created by SJP on 09/02/2020

import os

# Set the runID folder containing PO.csv files with incorrect header
# 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_3_MRYFR\\results\\110'
result_folder = 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_2_DPDMRY\\results\\133'
# PO name that is incorrect and needs to be replaced
mistake = 'STRING TO BE REPLACED'
# Corrected PO name to use as replacement
replacement = 'CORRECTED STRING'

for dir, subdirs, files in os.walk(result_folder):
    for f in files:
        if f.endswith('PO.csv'):
            filename = os.path.join(dir, f)

            # read in the file
            with open(filename, 'r') as opened_file:
                filedata = opened_file.read()

            # replace the target string
            if mistake in filedata:
                filedata = filedata.replace(mistake, replacement)
                print('Replacing mistake string in %s.' % filename)
            else:
                print('WARNING: could not find mistake string \"%s\" in %s.' % (mistake, filename))
            # write the file with corrected string
            with open(filename, 'w') as opened_file:
                opened_file.write(filedata)


