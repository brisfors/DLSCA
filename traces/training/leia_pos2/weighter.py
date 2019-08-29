import numpy as np

bla = np.load('leia_pos2_labels.npy')[:,0]

kla = [sum([x&(1<<i)>0 for i in range(32)]) for x in bla]

np.save('hammingWeights.npy',np.array(kla))
