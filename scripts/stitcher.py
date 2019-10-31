import numpy as np
import sys
import os
import glob
import gc

if len(sys.argv) != 3:
    sys.exit('Usage: ' + sys.argv[0] + ' input_dir output_prefix')
input_dir = sys.argv[1]
output_prefix = sys.argv[2]

# type name, input and output prefixes of the different types of series
suffixes = [
            ('traces', '_traces.npy', '_traces.npy'),
            ('keys', '_keylist.npy', '_keys.npy'),
            ('plaintexts', '_textin.npy', '_plaintexts.npy')
           ]

tracefiles = glob.glob(os.path.join(input_dir, '*' + suffixes[0][1]))
tracefiles.sort()

if len(tracefiles) == 0:
    sys.exit('No traces found in ' + input_dir)

for suffix in suffixes:
    f = output_prefix + suffix[2]
    if os.path.exists(f):
        sys.exit(f + ' exists')
    if os.access(f, os.W_OK):
        sys.exit(f + ' is not writable')

# verify that every trace has a key and pt file
i = len(tracefiles) - 1
while i != 0:
    basename = tracefiles[i][:-len(suffixes[0][1])]
    if not os.path.exists(basename + suffixes[1][1]):
        print(basename + ' is missing a keylist, skipping')
        tracefiles.pop(i)
    elif not os.path.exists(basename + suffixes[2][1]):
        print(basename + ' is missing a plaintext, skipping')
        tracefiles.pop(i)
    i -= 1

# concatenate types (traces, keys, pt) subsequently to save memory
for suffix in suffixes:
    (tname, isuf, osuf) = suffix

    # appending to a list is much faster than to a numpy array
    output, series = [], []
    for i, tf in enumerate(tracefiles):
        print('Appending ' + tname + ':{: .0%}'.format(i / (len(tracefiles) - 1)), end='\r')

        # adjust trace filename to current type
        f = tf[:-len(suffixes[0][1])] + isuf

        try:
            series[:] = np.load(f).flatten()
        except ValueError:
            sys.exit('Cannot load numpy array from file ' + f)
        output.append(series)
    print()

    output = np.array(output)
    assert output.shape[0] == len(tracefiles), 'Output shape looks wrong'
    np.save(output_prefix + osuf, output)
    gc.collect()
