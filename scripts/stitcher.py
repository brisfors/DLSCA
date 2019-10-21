import numpy as np
import sys
import os
import glob
import gc

if len(sys.argv) != 3:
    sys.exit('Usage: ' + sys.argv[0] + ' input_dir output_prefix')
input_dir = sys.argv[1]
output_prefix = sys.argv[2]

# the endings of the input and output files, the order matters
input_suffixes = ['_traces.npy', '_keylist.npy', '_textin.npy']
output_suffixes = ['_traces.npy', '_keys.npy', '_plaintexts.npy']

files = []
for i, suffix in enumerate(input_suffixes):
    files.insert(i, glob.glob(os.path.join(input_dir, '*' + suffix)))
    files[i].sort()

if len(files[0]) == 0:
    sys.exit('No traces found in ' + input_dir)
#if os.path.exists(output_file):
    #sys.exit(output_file + ' exists')
#if os.access(output_file, os.W_OK):
    #sys.exit(output_file + ' is not writable')

# verify that every trace has a key and pt file
for tracef in files[0]:
    basename = tracef[:-len(input_suffixes[0])]
    if not os.path.exists(basename + input_suffixes[1]):
        sys.exit(basename + ' is missing a keylist')
    if not os.path.exists(basename + input_suffixes[2]):
        sys.exit(basename + ' is missing a textin')

# appending to a list is much faster than to a numpy array
for i, suffix in enumerate(output_suffixes):
    output = [], []
    for f in files[i]:
        series[:] = np.load(os.path.join(input_dir, f)).flatten()
        output.append(series)
    output = np.array(output)
    print(output.shape)
    np.save(output_prefix + suffix, output)
    gc.collect()
